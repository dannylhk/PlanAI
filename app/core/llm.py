# app/core/llm.py
import os
from google import genai
from pydantic import BaseModel
from app.schemas.event import Event
from app.core.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_ID = "gemini-2.5-flash"

# Helper Schema for Intent Check
class IntentResponse(BaseModel):
    is_event_intent: bool

# The Intent Filter (Fast & Cheap)
async def check_event_intent(text: str) -> bool:
    """
    Determines if a message contains a plan/event intent.
    Used by Member B to filter noise.
    """
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"Analyze this chat message: '{text}'. \nDoes this message explicitly propose a specific plan, event, or meeting with a time or date? Return true only if it's a potential event.",
            config={
                "response_mime_type": "application/json",
                "response_schema": IntentResponse,
            },
        )
        return response.parsed.is_event_intent
    except Exception as e:
        print(f"⚠️ Intent Check Error: {e}")
        return False
    

# Extracttor
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
        print(f" Gemini Extraction Error: {e}")
        return None