"""
Bot Router - The Brain (Member B)
Routes messages to the correct handler based on chat type
"""
from typing import Dict, Any
from app.core.llm import extract_event_from_text, check_event_intent
from app.bot.responses import format_event_confirmation, send_message
from app.bot.date_utils import format_datetime

# MOCK DATA for Phase 3 Testing
# mock_enriched_event = {
#     "title": "CS2103T Lecture",
#     "start_time": "2026-01-17T14:00:00",
#     "location": "I3 Auditorium",
#     "web_enrichment": {
#         "summary": "Course website found.",
#         "url": "https://nus-cs2103.github.io/website/"
#     },
#     "conflict": False
# }

async def process_message(clean_data: Dict[str, Any]) -> None:
    """
    The brain of the bot - routes messages to the correct function.
    
    This is the critical routing logic that determines:
    - Private chat → Master Hub (Active command center)
    - Group chat → Listener (Passive event detection)
    
    Args:
        clean_data: The clean dictionary from parse_telegram_update containing:
            - chat_id: Where to send replies
            - user_id: Who sent the message
            - chat_type: "private", "group", or "supergroup"
            - text: The message content
    """
    
    chat_type = clean_data.get("chat_type")
    chat_id = clean_data.get("chat_id")
    user_id = clean_data.get("user_id")
    text = clean_data.get("text")
    
    print(f"\n🧠 ROUTER: Processing message from {chat_type} chat")
    print(f"   Chat ID: {chat_id}")
    print(f"   Text: {text}")
    
    # Route to the correct handler based on chat type
    if chat_type == "private":
        # This is a direct message to the bot - the "Master Hub"
        print("   → Routing to: Master Hub (handle_hub_command)")
        await handle_hub_command(text, user_id)
    
    elif "group" in chat_type:
        # This is a group or supergroup message - the "Listener"
        print("   → Routing to: Group Listener (handle_group_listener)")
        await handle_group_listener(text, chat_id, user_id)
    
    else:
        # Unknown chat type - this shouldn't happen, but be defensive
        print(f"   ⚠️ WARNING: Unknown chat_type '{chat_type}' - ignoring message")


async def handle_hub_command(text: str, user_id: int):
    """
    Handler for Master Hub (Private Chat).
    
    Supports:
    - /agenda: Show user's schedule for today
    - Natural language: "what is my plan today?"
    
    BEST PRACTICE (Software Engineering):
    - Start with simple print statements to verify the pipeline works
    - Add complexity incrementally (don't try to build everything at once)
    """
    print(f"\n💬 HUB: User {user_id} sent private command: {text}")
    
    # Step A: Input Normalization
    # Convert to lowercase and strip whitespace for consistent matching
    normalized_text = text.lower().strip()
    
    # Step B: The Guard Clause - Check for /agenda command
    # Support both strict command (/agenda) and natural language variants
    if normalized_text == "/agenda" or "my plan" in normalized_text:
        print("   📅 /agenda command detected")
        
        # Step C: The Date Context
        # Generate today's date in ISO 8601 format (YYYY-MM-DD) for Singapore timezone
        from datetime import datetime
        import pytz
        
        singapore_tz = pytz.timezone('Asia/Singapore')
        today = datetime.now(singapore_tz)
        date_string = today.strftime("%Y-%m-%d")
        
        print(f"   📆 Fetching events for: {date_string}")
        
        # Step D: The Data Retrieval (Mock for now)
        # TODO: Replace with: from app.services.crud import get_events_by_date
        # TODO: events = await get_events_by_date(user_id, date_string)
        
        # Mock data - realistic schedule for testing
        events = [
            {
                "start_time": "2026-01-18T09:00:00",
                "title": "CS2103T Lecture",
                "location": "I3 Auditorium",
                "conflict": False
            },
            {
                "start_time": "2026-01-18T14:00:00",
                "title": "Team Meeting",
                "location": "COM1-0210",
                "conflict": False
            },
            {
                "start_time": "2026-01-18T16:00:00",
                "title": "Gym Session",
                "location": None,  # Test null location handling
                "conflict": False
            }
        ]
        
        # For testing empty state, uncomment this:
        # events = []
        
        # Step E: Dispatch - Format and send the agenda
        from app.bot.responses import format_agenda, send_message
        
        agenda_message = format_agenda(events, date_string)
        await send_message(user_id, agenda_message)
        
        print("   ✅ Agenda sent to user")
        return
    
    # If not a recognized command, just log it for now
    print("   ⏭️  No command matched, ignoring...")


async def handle_group_listener(text: str, chat_id: int, user_id: int):
    """
    Phase 2: Group Listener
    
    Flow:
    1. Check if message contains event intent
    2. Extract event details using Member A's function
    3. Check for conflicts and save to database
    4. Send notification to user's private chat:
       - Success: Event saved with confirmation
       - Conflict: Event rejected with conflict details
    
    Args:
        text: The message text
        chat_id: The group chat ID (for logging)
        user_id: The user's ID (to send private notification)
    """

    print(f"\n👂 LISTENER: Heard '{text}' in Group {chat_id} from User {user_id}")
    
    # Step 1: Check if this message contains an event intent
    # Note: check_event_intent is now a synchronous keyword-based function (no await needed)
    is_event = check_event_intent(text)
    
    if not is_event:
        print("   ⏭️  Ignoring noise (not an event)...")
        return
    
    print("   ✅ Event Detected! Extracting details...")
    
    # Step 2: Extract event details using Member A's LLM function
    event = await extract_event_from_text(text)
    
    # DEFENSIVE PROGRAMMING: Check if extraction was successful
    if event is None:
        print("   ❌ ERROR: Failed to extract event details")
        return
    
    print(f"   📅 Extracted Event: {event.title} at {event.start_time}")
    
    # Step 3: Try to save to database (checks for conflicts internally)
    from app.services.crud import save_event_to_db
    
    save_result = await save_event_to_db(event)
    
    # Step 4: Send notification to user's private chat based on result
    if save_result["status"] == "success":
        print("   ✅ Event saved successfully! Notifying user...")
        await send_success_notification(user_id, event)
        
    elif save_result["status"] == "conflict":
        print(f"   ⚠️  CONFLICT DETECTED: {save_result['message']}")
        print("   ❌ Event NOT saved. Sending rejection notice...")
        await send_conflict_notification(user_id, event, save_result)
        
    else:
        print(f"   ❌ Database error: {save_result.get('message')}")
        await send_error_notification(user_id, event, save_result.get('message'))


async def send_success_notification(user_id: int, event):
    """
    Send success notification to user's private chat with Async UI pattern.
    
    Flow:
    1. Send loading message "🔍 Searching for venue info..."
    2. Enrich event with web search (Member A's agent)
    3. Edit loading message with final enriched result using format_event_card
    
    Args:
        user_id: The user's Telegram ID
        event: Event instance from extract_event_from_text() (Pydantic model)
    """
    from app.bot.responses import send_message, edit_message, format_event_card
    from app.core.agent import enrich_event
    
    # Step 1: Send loading message
    loading_msg = "🔍 <b>Processing your event...</b>\n\n⏳ Searching for additional information..."
    response = await send_message(user_id, loading_msg)
    
    if not response.get("ok"):
        print(f"   ❌ Failed to send loading message: {response.get('error')}")
        return
    
    # Get the message_id for editing later
    sent_msg_id = response.get("result", {}).get("message_id")
    if not sent_msg_id:
        print("   ❌ No message_id received from Telegram")
        return
    
    print(f"   📤 Loading message sent (message_id: {sent_msg_id})")
    
    # Step 2: Call Member A's enrichment agent (this is the slow part, 3-4 seconds)
    # enrich_event() takes an Event instance and returns an enriched Event instance
    try:
        enriched_event = await enrich_event(event)
        print(f"   ✨ Event enriched with web data")
    except Exception as e:
        print(f"   ⚠️ Enrichment failed: {e}, using original event")
        enriched_event = event
    
    # Step 3: Convert Event instance to dictionary for format_event_card
    event_data = enriched_event.model_dump()
    
    # Step 4: Format the final card (no conflict since we already saved successfully)
    final_text = format_event_card(event_data, has_conflict=False)
    
    # Step 5: Edit the loading message with the final result
    edit_result = await edit_message(user_id, sent_msg_id, final_text)
    
    if edit_result.get("ok"):
        print(f"   ✅ Loading message updated with final result!")
    else:
        print(f"   ❌ Failed to edit message: {edit_result.get('error')}")
        # Fallback: Send as new message if edit fails
        await send_message(user_id, final_text)


async def send_conflict_notification(user_id: int, event, conflict_info):
    """
    Send conflict rejection notice to user's private chat using format_event_card.
    
    The event was NOT saved due to conflicts, so we show the conflict warning.
    """
    from app.bot.responses import send_message, format_event_card
    
    conflicting_events = conflict_info.get("conflicting_events", [])
    
    # Convert Event to dict for format_event_card
    event_data = event.model_dump()
    
    # Use format_event_card with has_conflict=True
    card_message = format_event_card(event_data, has_conflict=True)
    
    # Add details about the conflicting events
    conflict_details = f"\n\n<b>Conflicting with:</b>"
    for idx, conflict in enumerate(conflicting_events[:3], 1):
        start_time_raw = conflict.get('start_time', 'N/A')
        start_time_formatted = format_datetime(start_time_raw) if start_time_raw != 'N/A' else 'N/A'
        conflict_details += f"\n{idx}. {conflict.get('title', 'Untitled')} ({start_time_formatted})"
    
    conflict_details += "\n\n💡 <i>Please choose a different time or cancel one of the conflicting events.</i>"
    
    final_message = card_message + conflict_details
    
    result = await send_message(user_id, final_message)
    
    if result.get("ok"):
        print(f"   ✅ Conflict notification sent to user {user_id}")
    else:
        print(f"   ❌ Failed to send notification: {result.get('error')}")


async def send_error_notification(user_id: int, event, error_msg):
    """Send error notification to user's private chat"""
    from app.bot.responses import send_message
    
    message = f"""
❌ <b>Error Adding Event</b>

Could not add: <b>{event.title}</b>

<b>Error:</b> {error_msg or 'Unknown error'}

Please try again later.
    """.strip()
    
    result = await send_message(user_id, message)
    
    if result.get("ok"):
        print(f"   ✅ Error notification sent to user {user_id}")
    else:
        print(f"   ❌ Failed to send notification: {result.get('error')}")
