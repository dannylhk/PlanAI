# app/core/llm.py
import os
from datetime import datetime, timedelta
from openai import AsyncOpenAI  # Use AsyncOpenAI for async functions
from pydantic import BaseModel, Field
from app.schemas.event import Event
from app.core.prompts import get_system_prompt
from dotenv import load_dotenv

load_dotenv()

# Initialize Async OpenAI Client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Use a standard OpenAI model ID
MODEL_ID = "gpt-4o"

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
        # Get fresh system prompt with current date (dynamic, not static import)
        system_prompt = get_system_prompt()
        
        # Using OpenAI's Beta Structured Outputs method
        completion = await client.beta.chat.completions.parse(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            response_format=Event,  # Directly passes the Pydantic class
        )
        
        event = completion.choices[0].message.parsed
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
        print(f"❌ OpenAI Extraction Error: {e}")
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

    try:
        completion = await client.beta.chat.completions.parse(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": f"The last event was '{prev_title}' at '{prev_time}'. Determine if the user is updating that event."},
                {"role": "user", "content": text}
            ],
            response_format=UpdateAnalysis,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"⚠️ Update detection failed: {e}")
        return UpdateAnalysis(is_update=False)
