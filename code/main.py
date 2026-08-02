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

    def process_message(self, message_row, user_context=""):
        """Asks Gemini to route a single message."""
        
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
        
        Decide the action, message_type, provide a reason, confidence, and any evidence_message_ids ('none' for now).
        """
        
        # Call Gemini and force the output to match our Pydantic schema
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
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
        users_df = pd.read_csv("dataset/users.csv")
        # We set user_id as index so we can look up users instantly
        users_df.set_index("user_id", inplace=True) 
    except FileNotFoundError as e:
        print(f"Error: Could not find dataset files. Make sure you are running from the project root. ({e})")
        return

    agent = RouterAgent()
    
    # Test first 3 messages
    print("\n--- Testing the Bouncer on the first 3 messages ---\n")
    
    for index, row in messages_df.head(3).iterrows():
        print(f"Processing {row['message_id']}...")
        
        user_context = "No specific user context found."
        user_id = row['user_id']
        if user_id in users_df.index:
            user_data = users_df.loc[user_id]
            user_context = f"User has Do Not Disturb window: {user_data.get('do_not_disturb_window', 'None')}"
            
        # Get the AI's decision
        try:
            decision = agent.process_message(row, user_context)
            
            print(f"  TEXT:   {row['message_text'][:60]}...")
            print(f"  ACTION: {decision['action'].upper()} (Type: {decision['message_type']})")
            print(f"  REASON: {decision['reason']}")
            print("-" * 50)
            
        except Exception as e:
            print(f"  Error processing message: {e}")

if __name__ == "__main__":
    main()