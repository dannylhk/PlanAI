# app/core/llm.py
import os
from datetime import datetime, timedelta
from google import genai
from pydantic import BaseModel, Field
from app.schemas.event import Event
from app.core.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_ID = "gemini-2.5-flash-lite"

def check_event_intent(text: str) -> bool:
    """
    Keyword-based intent check (Fast Gate).
    Filters out noise before any API calls are made.
    """
    event_keywords = [
        "meet", "meeting", "event", "class", "lecture", "dinner", "lunch", 
        "tomorrow", "today", "next", "at", "pm", "am", "friday", "monday", 
        "schedule", "change", "actually", "move", "instead", "push", "cancel"
    ]
    
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
    


class UpdateAnalysis(BaseModel):
    """Schema for Phase 5 Update Intelligence"""
    is_update: bool = Field(False, description="True if the user is modifying a previous event.")
    new_start_time: str | None = Field(None, description="ISO 8601 start time if changed.")
    new_location: str | None = Field(None, description="New location if changed.")
    new_title: str | None = Field(None, description="New title if changed.")

async def detect_update_intent(text: str, context: dict) -> UpdateAnalysis:
    """
    Member A: Optimized update detection.
    Uses local keyword checking to decide if an LLM call is actually necessary.
    """
    if not context:
        return UpdateAnalysis(is_update=False)

    # Internal optimization: Only call LLM if update-specific keywords are present
    update_triggers = ["change", "actually", "move", "instead", "push", "edit", "correct"]
    text_lower = text.lower()
    
    # If no update-specific keywords are found, assume it's a new event attempt
    if not any(trigger in text_lower for trigger in update_triggers):
        return UpdateAnalysis(is_update=False)

    prev_title = context.get('title', 'Unknown')
    prev_time = context.get('start_time', 'Unknown')

    prompt = f"""
    CONTEXT: Last event was '{prev_title}' at '{prev_time}'.
    USER MESSAGE: "{text}"
    TASK: Is the user updating that event? Return JSON with is_update: true and extracted changes.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": UpdateAnalysis,
            },
        )
        return response.parsed
    except Exception as e:
        print(f"⚠️ Update detection failed: {e}")
        return UpdateAnalysis(is_update=False)
