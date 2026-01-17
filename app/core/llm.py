# app/core/llm.py
import os
from datetime import datetime, timedelta
from google import genai
from pydantic import BaseModel
from app.schemas.event import Event
from app.core.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_ID = "gemini-2.5-flash-lite"

# Helper Schema for Intent Check
class IntentResponse(BaseModel):
    is_event_intent: bool

# The Intent Filter (Fast & Cheap)
# async def check_event_intent(text: str) -> bool:
#     """
#     Determines if a message contains a plan/event intent.
#     Used by Member B to filter noise.
#     """
#     try:
#         response = client.models.generate_content(
#             model=MODEL_ID,
#             contents=f"Analyze this chat message: '{text}'. \nDoes this message explicitly propose a specific plan, event, or meeting with a time or date? Return true only if it's a potential event.",
#             config={
#                 "response_mime_type": "application/json",
#                 "response_schema": IntentResponse,
#             },
#         )
#         return response.parsed.is_event_intent
#     except Exception as e:
#         print(f"⚠️ Intent Check Error: {e}")
#         return False
# In app/core/llm.py - Replace the async function
def check_event_intent(text: str) -> bool:
    """Simple keyword-based intent check (no API call)"""
    event_keywords = ["meet", "meeting", "event", "class", "lecture", 
                      "dinner", "lunch", "tomorrow", "today", "next", 
                      "at", "pm", "am", "friday", "monday"]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in event_keywords)

    

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
        event = response.parsed 

    # --- NEW LOGIC: DEFAULT 1 HOUR DURATION ---
        if event.start_time and not event.end_time:
            try:
                # 1. Parse the string into a datetime object
                start_dt = datetime.fromisoformat(event.start_time)
                
                # 2. Add 1 hour
                end_dt = start_dt + timedelta(hours=1)
                
                # 3. Convert back to ISO string
                event.end_time = end_dt.isoformat()
                
                print(f"   🕒 Added default end time: {event.end_time}")
            except ValueError:
                print("   ⚠️ Could not parse start_time to calculate duration")
        # ------------------------------------------
        return event
    
    except Exception as e:
        print(f" Gemini Extraction Error: {e}")
        return None
