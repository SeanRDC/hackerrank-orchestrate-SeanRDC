import os
from dotenv import load_dotenv
from google import genai

# Load the secret API key
load_dotenv()

# Initialize Gemini
client = genai.Client()

# test purposes. Ask gemini simple question
print("Sending message to Gemini...")
response = client.models.generate_content(
    model='gemini-3.5-flash-lite',
    contents='Hello, Gemini! Are you ready to be a bouncer for my nightclub?'
)

print("\nGemini says:")
print(response.text)