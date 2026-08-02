import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

class RoutingDecision(BaseModel):
    action: str = Field(description="Must be one of: notify, digest, mute")
    message_type: str = Field(description="Must be one of: personal, urgent, event, payment, business_update, promotion, greeting, forward, spam, scam, unknown")
    reason: str = Field(description="Short human-readable explanation for the decision")
    confidence: float = Field(description="Number from 0.0 to 1.0")
    evidence_message_ids: str = Field(description="Semicolon-separated historical message IDs used as evidence, or 'none'")

class RouterAgent:
    """Uses Google GenAI to process inputs and route notifications."""
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-3.5-flash-lite"
        
        # System instructions set the "personality" and strict rules
        self.system_instruction = (
            "You are an AI notification router for WhatsApp. Your job is to decide whether an incoming message "
            "should 'notify' (interrupt the user now), 'digest' (wait for later), or 'mute' (suppress as unwanted/unsafe). "
            "Make personalized decisions based on the context provided. Always return valid JSON matching the schema."
        )

    def process_message(self, message_row, user_context="", business_context="", group_context="", media_path=None):
        """Asks Gemini to route a single message with rich context and media."""
        
        # Construct the prompt with the specific message details
        prompt = f"""
        Please route the following incoming message.
        
        MESSAGE DETAILS:
        Message ID: {message_row['message_id']}
        From Sender: {message_row['sender_user_id']} (Business ID: {message_row['business_id']}, Group ID: {message_row['group_id']})
        To User: {message_row['user_id']}
        Type: {message_row['conversation_type']}
        Time: {message_row['created_at']}
        Forwarded Count: {message_row['forwarded_count']}
        Text Content: "{message_row['message_text']}"
        
        RECEIVER CONTEXT:
        {user_context}

        BUSINESS CONTEXT:
        {business_context}

        GROUP CONTEXT:
        {group_context}
        
        Decide the action, message_type, provide a reason, confidence, and any evidence_message_ids ('none' for now).
        """
        
        contents_list = [prompt]
        
        if media_path and os.path.exists(media_path):
            print(f"    [Uploading media file to Gemini: {media_path}]")
            media_file = self.client.files.upload(file=media_path)
            contents_list.append(media_file)

        # Call Gemini and force the output to match our Pydantic schema
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents_list,
            config=genai.types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json",
                response_schema=RoutingDecision,
                temperature=0.2,
            ),
        )
        
        return json.loads(response.text)

def main():
    print("Starting HackerRank Orchestrate: Message Notification Router...")
    
    # Load dataset
    print("Loading datasets...")
    try:
        messages_df = pd.read_csv("dataset/messages.csv")
        users_df = pd.read_csv("dataset/users.csv").set_index("user_id")
        groups_df = pd.read_csv("dataset/groups.csv").set_index("group_id")
        business_df = pd.read_csv("dataset/business_accounts.csv").set_index("business_id")
        images_df = pd.read_csv("dataset/images.csv").set_index("image_id")
        voice_df = pd.read_csv("dataset/voice_notes.csv").set_index("voice_note_id")
    except FileNotFoundError as e:
        print(f"Error: Could not find dataset files. Make sure you are running from the project root. ({e})")
        return

    agent = RouterAgent()
    
    # Test the first 15 messages to include audio and img
    print("\n--- Testing the Bouncer on the first 15 messages ---\n")
    
    for index, row in messages_df.head(15).iterrows():
        print(f"Processing {row['message_id']}...")
        
        # Build Contexts safely
        user_context = "None"
        if pd.notna(row['user_id']) and row['user_id'] in users_df.index:
            user_context = str(users_df.loc[row['user_id']].to_dict())

        business_context = "None"
        if pd.notna(row['business_id']) and row['business_id'] in business_df.index:
            business_context = str(business_df.loc[row['business_id']].to_dict())

        group_context = "None"
        if pd.notna(row['group_id']) and row['group_id'] in groups_df.index:
            group_context = str(groups_df.loc[row['group_id']].to_dict())

        # Resolve Media Path
        media_path = None
        if row['media_type'] == 'image' and pd.notna(row['media_id']):
            if row['media_id'] in images_df.index:
                media_path = "dataset/" + images_df.loc[row['media_id']]['file_path']
        elif row['media_type'] == 'voice' and pd.notna(row['media_id']):
            if row['media_id'] in voice_df.index:
                media_path = "dataset/" + voice_df.loc[row['media_id']]['file_path']

        # Get the AI's decision
        try:
            decision = agent.process_message(row, user_context, business_context, group_context, media_path)
            
            print(f"  TEXT:   {str(row['message_text'])[:60]}...") 
            print(f"  MEDIA:  {media_path}")
            print(f"  ACTION: {decision['action'].upper()} (Type: {decision['message_type']})")
            print(f"  REASON: {decision['reason']}")
            print("-" * 50)
            
        except Exception as e:
            print(f"  Error processing message: {e}")

if __name__ == "__main__":
    main()