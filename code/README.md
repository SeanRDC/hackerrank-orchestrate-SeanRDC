# Message Notification Router - AI Agent

This repository contains an AI-powered message notification router built for the HackerRank Orchestrate hackathon. It utilizes Google's Gemini AI to intelligently classify and route WhatsApp messages based on multimodal inputs (text, images, audio) and historical user context.

## Architecture

The system is contained within `main.py` and operates in four stages:

1. **Data Loading:** Loads all contextual datasets (`users`, `groups`, `business_accounts`, `history`) into memory using Pandas.
2. **Context Assembly:** For each incoming message, the script gathers specific receiver behavior, sender trust scores, and fetches the last 3 interactions between the entities as evidence.
3. **Multimodal Inference:** Uploads any associated image (`.jpg`) or audio (`.mp3`) files to the Gemini API.
4. **Structured Routing:** Prompts `gemini-3.5-flash-lite` to evaluate the raw message + context and return a strict JSON schema deciding whether to `notify`, `digest`, or `mute`.

## Setup Instructions

1. Ensure you have Python 3.8+ installed.
2. Install the required dependencies:
    ```bash
   pip install google-genai pandas python-dotenv
3. Create a .env file in the root directory and add your Google Gemini API key:
    ```bash
    GEMINI_API_KEY="your_api_key_here"

## Run Instructions
1. Execute the main orchestrator script from the root of the repository:
    ```bash
    python code/main.py