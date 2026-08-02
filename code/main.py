import os
import json
import time
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
        
        self.system_instruction = (
            "You are an AI notification router for WhatsApp. Your job is to decide whether an incoming message "
            "should 'notify' (interrupt the user now), 'digest' (wait for later), or 'mute' (suppress as unwanted/unsafe). "
            "Use the provided context (User, Business, Group, History) to make a personalized decision. "
            "If the message is a scam, phishing attempt, or unsafe, always action as 'mute' and set type to 'scam' or 'spam'. "
            "Your output must exactly match the required JSON schema."
        )

    def process_message(self, message_row, user_context="", business_context="", group_context="", history_context="", media_path=None):
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
        
        HISTORICAL INTERACTION EVIDENCE (Past messages from this sender to this user):
        {history_context}
        
        Decide the action, message_type, provide a reason, confidence, and any evidence_message_ids ('none' for now).
        """
        
        contents_list = [prompt]
        
        if media_path and os.path.exists(media_path):
            print(f"    [Uploading media file to Gemini: {media_path}]")
            media_file = self.client.files.upload(file=media_path)
            contents_list.append(media_file)

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
        history_df = pd.read_csv("dataset/message_history.csv")
        events_df = pd.read_csv("dataset/message_events.csv")
        merged_history = pd.merge(history_df, events_df, on=['message_id', 'user_id'], how='left')
        
    except FileNotFoundError as e:
        print(f"Error: Could not find dataset files. Make sure you are running from the project root. ({e})")
        return

    agent = RouterAgent()
    
    results = []
    total_messages = len(messages_df)
    
    for index, row in messages_df.iterrows():
        print(f"Processing {index + 1}/{total_messages}: {row['message_id']}...")
        
        user_context = "None"
        if pd.notna(row['user_id']) and row['user_id'] in users_df.index:
            user_context = str(users_df.loc[row['user_id']].to_dict())

        business_context = "None"
        if pd.notna(row['business_id']) and row['business_id'] in business_df.index:
            business_context = str(business_df.loc[row['business_id']].to_dict())

        group_context = "None"
        if pd.notna(row['group_id']) and row['group_id'] in groups_df.index:
            group_context = str(groups_df.loc[row['group_id']].to_dict())

        # Build History Context
        history_context = "None"
        user_history = merged_history[merged_history['user_id'] == row['user_id']]
        if pd.notna(row['business_id']):
            relevant_hist = user_history[user_history['business_id'] == row['business_id']]
        elif pd.notna(row['group_id']):
            relevant_hist = user_history[user_history['group_id'] == row['group_id']]
        else:
            relevant_hist = user_history[user_history['sender_user_id'] == row['sender_user_id']]
            
        if not relevant_hist.empty:
            recent_history = relevant_hist.tail(3)
            hist_records = []
            for _, h_row in recent_history.iterrows():
                record = f"ID:{h_row['message_id']} | Text: '{str(h_row['message_text'])[:50]}...' | Opened:{h_row['message_opened']} | Muted:{h_row['muted_after_message']} | Dismissed:{h_row['notification_dismissed']}"
                hist_records.append(record)
            history_context = "\n".join(hist_records)

        # Resolve Media Path
        media_path = None
        if row['media_type'] == 'image' and pd.notna(row['media_id']):
            if row['media_id'] in images_df.index:
                media_path = "dataset/" + images_df.loc[row['media_id']]['file_path']
        elif row['media_type'] == 'voice' and pd.notna(row['media_id']):
            if row['media_id'] in voice_df.index:
                media_path = "dataset/" + voice_df.loc[row['media_id']]['file_path']

        # Get the AI's decision with a retry loop for rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                decision = agent.process_message(row, user_context, business_context, group_context, history_context, media_path)
                
                # Store result for our output
                results.append({
                    "message_id": row['message_id'],
                    "action": decision['action'].lower(),
                    "message_type": decision['message_type'].lower(),
                    "reason": decision['reason'],
                    "confidence": decision['confidence'],
                    "evidence_message_ids": decision['evidence_message_ids']
                })
                
                # Give the API a 4-second breather to respect the 15 Requests Per Minute free tier limit
                time.sleep(4)
                break
                
            except Exception as e:
                error_msg = str(e).lower()
                # Check if the error is a rate limit
                if "429" in error_msg or "exhausted" in error_msg or "quota" in error_msg:
                    if attempt < max_retries - 1:
                        print(f"    [!] Rate limit hit. Pausing for 15 seconds before retrying (Attempt {attempt+1}/{max_retries})...")
                        time.sleep(15)
                    else:
                        print(f"    [!] Rate limit completely exhausted for {row['message_id']}. Skipping.")
                        results.append({
                            "message_id": row['message_id'],
                            "action": "digest",
                            "message_type": "unknown",
                            "reason": f"API Rate Limit Exhausted",
                            "confidence": 0.0,
                            "evidence_message_ids": "none"
                        })
                else:
                    print(f"  Error processing message: {e}")
                    # Fallback row for standard errors
                    results.append({
                        "message_id": row['message_id'],
                        "action": "digest",
                        "message_type": "unknown",
                        "reason": f"API Error: {e}",
                        "confidence": 0.0,
                        "evidence_message_ids": "none"
                    })
                    break

    # Save to output.csv
    print("\nSaving results to dataset/output.csv...")
    output_df = pd.DataFrame(results)
    
    # Arranged columns
    output_df = output_df[["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]]
    output_df.to_csv("dataset/output.csv", index=False)
    

if __name__ == "__main__":
    main()