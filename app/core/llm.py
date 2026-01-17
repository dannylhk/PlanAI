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

def check_event_intent(text: str) -> bool:
    """Simple keyword-based intent check (no API call)"""
    event_keywords = ["meet", "meeting", "event", "class", "lecture", 
                      "dinner", "lunch", "tomorrow", "today", "next", 
                      "at", "pm", "am", "friday", "monday", "schedule"]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in event_keywords)

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

        if not event:
            return None

        # --- VALIDATION: PAST EVENT BLOCKER ---
        try:
            start_dt = datetime.fromisoformat(event.start_time)
            now = datetime.now()
            
            # If event is in the past (with 5 min buffer for latency), reject it
            if start_dt < (now - timedelta(minutes=5)):
                print(f"   🚫 Blocked past event: {event.start_time} < {now}")
                return None
                
            # --- DEFAULT DURATION LOGIC ---
            if not event.end_time:
                # Add 1 hour default
                end_dt = start_dt + timedelta(hours=1)
                event.end_time = end_dt.isoformat()
                print(f"   🕒 Added default end time: {event.end_time}")
                
        except ValueError:
            print("   ⚠️ Date parsing error during validation")
            # We proceed; let the DB handle strict format errors if needed
            
        return event
    
    except Exception as e:
        print(f" Gemini Extraction Error: {e}")
        return None
