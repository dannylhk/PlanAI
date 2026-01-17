# app/core/llm.py
import os
from dotenv import load_dotenv
from google import genai
from app.schemas.event import Event
from app.core.prompts import SYSTEM_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_ID = "gemini-2.5-flash"

async def extract_event_from_text(text: str) -> Event | None:
    try:
        response = client.models.generate_content(
            model=MODEL_ID, 
            contents=f"{SYSTEM_PROMPT}\n\nUSER MESSAGE:\n{text}",
            config={
                "response_mime_type": "application/json",
                "response_schema": Event,
            },
        )
        return response.parsed 
    except Exception as e:
        print(f"❌ Gemini Extraction Error: {e}")
        return None