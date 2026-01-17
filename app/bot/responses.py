"""
Telegram Response Utilities (Member B)
Functions for sending formatted messages back to Telegram
"""

import os
import httpx
from typing import Dict, Any
from app.schemas.event import Event
from dotenv import load_dotenv

load_dotenv()

# Get bot token from environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def send_message(chat_id: int, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
    """
    Send a message to a Telegram chat.
    
    Args:
        chat_id: The chat ID (can be user ID or group ID)
        text: The message text to send
        parse_mode: "HTML" or "Markdown" for formatting
        
    Returns:
        The response from Telegram API
        
    BEST PRACTICE:
    - Always use async for network calls (non-blocking)
    - Use HTML formatting for better control over message appearance
    - Handle errors gracefully (don't crash if Telegram is down)
    """
    url = f"{TELEGRAM_API_URL}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            return response.json()
    except Exception as e:
        print(f"❌ Error sending message to Telegram: {e}")
        return {"ok": False, "error": str(e)}


def format_event_confirmation(event: Event) -> str:
    """
    Format an Event object into a human-readable confirmation message.
    
    Args:
        event: The Event Pydantic model instance
        
    Returns:
        A formatted HTML string for Telegram
        
    HOW TO USE EVENT DATA:
    - Event is a Pydantic model (like a class instance)
    - Access fields with: event.title, event.start_time, etc.
    - Convert to dict: event.model_dump() or event.dict()
    - Convert to JSON string: event.model_dump_json()
    
    BEST PRACTICE:
    - Use HTML formatting for better readability
    - Include emojis for visual appeal
    - Show all important info at a glance
    """
    
    # Access Event fields directly (they're class attributes)
    title = event.title
    start_time = event.start_time
    end_time = event.end_time
    location = event.location or "Not specified"
    
    # Format the message with HTML
    message = f"""
📅 <b>Event Detected!</b>

<b>Title:</b> {title}
<b>Start:</b> {start_time}
<b>End:</b> {end_time}
<b>Location:</b> {location}

<i>Reply with /confirm to add this to your calendar</i>
    """.strip()
    
    return message


def format_event_summary(event: Event) -> str:
    """
    Format an Event for the Master Hub (Private Chat) - more detailed view.
    
    This includes web enrichment data if available.
    """
    
    message = f"""
✅ <b>Event Added to Your Calendar</b>

📌 <b>{event.title}</b>
🕐 <b>Start:</b> {event.start_time}
🕐 <b>End:</b> {event.end_time}
📍 <b>Location:</b> {event.location or 'Not specified'}
    """.strip()
    
    # Add web enrichment if available
    if event.web_enrichment:
        message += "\n\n🔗 <b>Additional Info:</b>"
        
        if isinstance(event.web_enrichment, dict):
            if url := event.web_enrichment.get("url"):
                message += f"\n• Link: {url}"
            if map_link := event.web_enrichment.get("map_link"):
                message += f"\n• Map: {map_link}"
            if summary := event.web_enrichment.get("summary"):
                message += f"\n• {summary}"
    
    return message


async def send_event_confirmation(chat_id: int, event: Event) -> Dict[str, Any]:
    """
    MAIN FUNCTION: Send an event confirmation to a Telegram group.
    
    This is what you call in handle_group_listener after extracting the event.
    
    Args:
        chat_id: The group chat ID
        event: The Event object from Member A's extract_event_from_text()
        
    Returns:
        Telegram API response
        
    Example usage in router.py:
    ```python
    from app.core.llm import extract_event_from_text
    from app.bot.responses import send_event_confirmation
    
    # After detecting "meet" in the message:
    event = await extract_event_from_text(text)  # Returns Event object
    await send_event_confirmation(chat_id, event)  # Send to group
    ```
    """
    formatted_message = format_event_confirmation(event)
    return await send_message(chat_id, formatted_message)


async def send_event_notification(chat_id: int, event: Event) -> Dict[str, Any]:
    """
    Send a detailed event notification to the Master Hub (Private Chat).
    
    Called after user confirms the event in the group.
    """
    formatted_message = format_event_summary(event)
    return await send_message(chat_id, formatted_message)


# ==============================================================================
# UNDERSTANDING: Event Object vs JSON
# ==============================================================================

"""
❓ QUESTION: "I assume it's in JSON format, how should I send it?"

✅ ANSWER: Event is NOT JSON - it's a Pydantic model (Python object).

Here's the breakdown:

1. WHAT IS AN EVENT?
   - It's a Python class instance (like a custom data type)
   - Created by Member A's extract_event_from_text() function
   - Has attributes: event.title, event.start_time, etc.

2. HOW TO ACCESS EVENT DATA?
   
   # Access fields directly:
   title = event.title
   time = event.start_time
   
   # Convert to dictionary:
   event_dict = event.model_dump()  # or event.dict() in older Pydantic
   
   # Convert to JSON string:
   event_json = event.model_dump_json()  # Returns: '{"title": "...", ...}'
   
   # Convert back from dict to Event:
   event = Event(**event_dict)

3. HOW TO SEND TO TELEGRAM?
   
   ❌ DON'T send raw JSON to users:
   await send_message(chat_id, event.model_dump_json())
   # User sees: {"title": "CS2103", "start_time": "2026-01-24T14:00:00", ...}
   # Ugly and confusing!
   
   ✅ DO format it nicely first:
   formatted = format_event_confirmation(event)
   await send_message(chat_id, formatted)
   # User sees: 
   # 📅 Event Detected!
   # Title: CS2103
   # Start: 2026-01-24T14:00:00
   # Much better!

4. THE COMPLETE FLOW:
   
   Step 1: Member A extracts event from text
   -------
   event = await extract_event_from_text("Let's meet Friday at 2pm")
   # Returns: Event(title="Meeting", start_time="2026-01-24T14:00:00", ...)
   
   Step 2: You format it nicely
   -------
   message = format_event_confirmation(event)
   # Returns: "📅 Event Detected!\n\nTitle: Meeting\n..."
   
   Step 3: You send it to Telegram
   -------
   await send_message(chat_id, message)
   # Telegram displays the formatted message to users

5. WHY USE PYDANTIC INSTEAD OF RAW DICTS?
   
   ✅ Type safety: event.title is guaranteed to be a string
   ✅ Validation: Pydantic checks if start_time is in correct format
   ✅ Auto-completion: Your IDE knows what fields exist
   ✅ Easy conversion: Can convert to/from JSON, dict, database rows
   
   Example:
   # This will FAIL with clear error:
   event = Event(title=123, start_time="invalid")
   # Pydantic: "title must be a string, start_time must be ISO 8601"
   
   # This will SUCCEED:
   event = Event(title="Meeting", start_time="2026-01-24T14:00:00")
"""
