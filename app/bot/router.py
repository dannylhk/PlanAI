"""
Bot Router - The Brain (Member B)
Routes messages to the correct handler based on chat type
"""
from typing import Dict, Any, List
from app.core.llm import extract_event_from_text, check_event_intent, detect_update_intent
from app.bot.responses import format_event_confirmation, send_message, edit_message
from app.bot.date_utils import format_datetime
from app.core.agent import scavenge_events
from app.services.crud import save_scavenged_events_batch
from app.schemas.event import Event

# ============================================================================
# PHASE 5: IN-MEMORY CONTEXT STORE (Short-Term Memory)
# ============================================================================
# chat_context structure:
# {
#     chat_id (int): event_id (int)
# }
# This tracks the last successfully confirmed event in each group chat.
chat_context: Dict[int, int] = {}

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
    
    # ========================================================================
    # CLEARALL: Clear all events for today and send a goofy rest message
    # ========================================================================
    if normalized_text == "/clearall":
        print("   🗑️ /clearall command detected")
        await handle_clearall_command(user_id)
        return
    
    # ========================================================================
    # PHASE 7: /force_briefing - Demo Command for Nightly Briefing
    # ========================================================================
    if normalized_text == "/force_briefing":
        print("   🌙 /force_briefing command detected (DEMO)")
        await handle_force_briefing(user_id)
        return
    
    # ========================================================================
    # PHASE 6: /track [topic] - Active Research Mode
    # ========================================================================
    if normalized_text.startswith("/track"):
        print("   🕵️ /track command detected")
        await handle_track_command(text, user_id)
        return
    
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
        
        # Step D: The Data Retrieval - Query real database
        from app.services.crud import get_events_by_date
        events = await get_events_by_date(user_id, date_string)
        
        print(f"   📊 Found {len(events)} events for today")
        
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
    Phase 5: Group Listener with Statefulness
    
    Flow:
    1. Check if message contains event intent (time-related keywords)
    2. If there is previous context for this group:
       - Check if this is an update to the previous event
       - If yes, handle update confirmation flow
    3. If no context OR not an update:
       - Create new event and save to database
       - Store event ID in chat_context for future updates
    
    Args:
        text: The message text
        chat_id: The group chat ID (for context lookup)
        user_id: The user's ID (to send private notification)
    """
    global chat_context
    
    print(f"\n👂 LISTENER: Heard '{text}' in Group {chat_id} from User {user_id}")
    
    # ========================================================================
    # STEP 1: Check if this is time-related (event intent)
    # ========================================================================
    is_event = check_event_intent(text)
    
    if not is_event:
        print("   ⏭️  Ignoring noise (not time-related)...")
        return
    
    print("   ✅ Time-related message detected!")
    
    # ========================================================================
    # STEP 2: Check if there is previous context for this group
    # ========================================================================
    if chat_id in chat_context:
        print(f"   🧠 Memory found! Last event ID: {chat_context[chat_id]}")
        
        # Retrieve the previous event from database
        from app.services.crud import get_event_by_id
        previous_event = await get_event_by_id(chat_context[chat_id])
        
        if previous_event:
            print(f"   📋 Previous event: {previous_event.get('title')} at {previous_event.get('start_time')}")
            
            # Check if this message is trying to update the previous event
            update_analysis = await detect_update_intent(text, previous_event)
            
            if update_analysis.is_update:
                print("   🔄 UPDATE INTENT DETECTED!")
                # Handle update confirmation flow
                await handle_update_confirmation(user_id, chat_id, previous_event, update_analysis, text)
                return
            else:
                print("   ➕ Not an update - treating as new event")
        else:
            print("   ⚠️ Previous event not found in database - treating as new event")
    else:
        print("   🆕 No previous context for this group")
    
    # ========================================================================
    # STEP 3: Create new event (no context OR not an update)
    # ========================================================================
    print("   🆕 Creating new event...")
    
    event = await extract_event_from_text(text)
    
    if event is None:
        print("   ❌ ERROR: Failed to extract event details")
        return
    
    print(f"   📅 Extracted Event: {event.title} at {event.start_time}")
    
    # Save to database
    from app.services.crud import save_event_to_db
    save_result = await save_event_to_db(event, user_id=user_id)
    
    # Handle save result
    if save_result["status"] == "success":
        print("   ✅ Event saved successfully!")
        
        # CRITICAL: Save event ID to chat_context for future updates
        event_id = save_result["data"].get("id")
        if event_id:
            chat_context[chat_id] = event_id
            print(f"   🧠 Stored event ID {event_id} in chat_context for group {chat_id}")
        
        await send_success_notification(user_id, event)
        
    elif save_result["status"] == "conflict":
        print(f"   ⚠️  CONFLICT DETECTED: {save_result['message']}")
        await send_conflict_notification(user_id, event, save_result)
        
    else:
        print(f"   ❌ Database error: {save_result.get('message')}")
        await send_error_notification(user_id, event, save_result.get('message'))


async def handle_update_confirmation(user_id: int, chat_id: int, previous_event: dict, update_analysis, original_text: str):
    """
    Handle the update confirmation flow.
    
    Sends a message to the user asking for confirmation of the detected update.
    
    NOTE: In a full implementation, this would use Telegram inline keyboard buttons
    or wait for a confirmation response. For the hackathon, we'll auto-apply updates
    with a clear notification.
    
    Args:
        user_id: The user's Telegram ID
        chat_id: The group chat ID
        previous_event: The previous event data from database
        update_analysis: UpdateAnalysis from detect_update_intent
        original_text: The original message text
    """
    from app.bot.responses import send_message
    from app.services.crud import update_event
    
    print(f"\n🔄 HANDLING UPDATE CONFIRMATION for event {previous_event.get('id')}")
    
    # Build the update dictionary from the analysis
    updates = {}
    changes_text = []
    
    if update_analysis.new_start_time:
        updates["start_time"] = update_analysis.new_start_time
        old_time = format_datetime(previous_event.get('start_time', 'N/A'))
        new_time = format_datetime(update_analysis.new_start_time)
        changes_text.append(f"⏰ Time: {old_time} → {new_time}")
    
    if update_analysis.new_location:
        updates["location"] = update_analysis.new_location
        old_loc = previous_event.get('location', 'Not specified')
        changes_text.append(f"📍 Location: {old_loc} → {update_analysis.new_location}")
    
    if update_analysis.new_title:
        updates["title"] = update_analysis.new_title
        old_title = previous_event.get('title', 'Untitled')
        changes_text.append(f"📝 Title: {old_title} → {update_analysis.new_title}")
    
    if not updates:
        print("   ⚠️ Update detected but no fields to change")
        message = f"""
🤔 <b>Update Detected</b>

I noticed you might be updating:
<b>{previous_event.get('title', 'Your event')}</b>

But I couldn't determine what to change. Please be more specific!

<i>Your message: "{original_text}"</i>
        """.strip()
        await send_message(user_id, message)
        return
    
    # Perform the update
    print(f"   📝 Applying updates: {updates}")
    update_result = await update_event(previous_event.get('id'), updates)
    
    if update_result["status"] == "success":
        print("   ✅ Event updated successfully!")
        
        changes_list = "\n".join(changes_text)
        message = f"""
✅ <b>Event Updated!</b>

<b>{update_result['data'].get('title', 'Your event')}</b>

<b>Changes applied:</b>
{changes_list}

<i>Original message: "{original_text}"</i>
        """.strip()
        
        await send_message(user_id, message)
        
    elif update_result["status"] == "conflict":
        print(f"   ⚠️ UPDATE CONFLICT: {update_result['message']}")
        
        changes_list = "\n".join(changes_text)
        conflicting_events = update_result.get("conflicting_events", [])
        
        conflict_details = ""
        for idx, conflict in enumerate(conflicting_events[:3], 1):
            start_time_raw = conflict.get('start_time', 'N/A')
            start_time_formatted = format_datetime(start_time_raw) if start_time_raw != 'N/A' else 'N/A'
            conflict_details += f"\n{idx}. {conflict.get('title', 'Untitled')} ({start_time_formatted})"
        
        message = f"""
⚠️ <b>Update Failed - Conflict Detected</b>

<b>{previous_event.get('title', 'Your event')}</b>

<b>Attempted changes:</b>
{changes_list}

<b>Conflicts with:</b>
{conflict_details}

💡 <i>The event was NOT updated. Please choose a different time.</i>
        """.strip()
        
        await send_message(user_id, message)
        
    else:
        print(f"   ❌ Update error: {update_result.get('message')}")
        message = f"""
❌ <b>Update Failed</b>

Could not update: <b>{previous_event.get('title', 'Your event')}</b>

<b>Error:</b> {update_result.get('message', 'Unknown error')}

Please try again later.
        """.strip()
        
        await send_message(user_id, message)


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


# ============================================================================
# CLEARALL: Clear all events for today - The Ultimate Rest Mode
# ============================================================================

async def handle_clearall_command(user_id: int):
    """
    Clears all events for the current day and sends a goofy message
    encouraging the user to take a break and rest.
    
    Usage: Send "/clearall" to the bot in private chat
    
    Args:
        user_id: The user's Telegram ID
    """
    from datetime import datetime
    import pytz
    import random
    from app.services.crud import delete_events_by_date
    
    print(f"\n🗑️ CLEARALL: User {user_id} wants to clear today's events")
    
    # Get today's date in Singapore timezone
    singapore_tz = pytz.timezone('Asia/Singapore')
    today = datetime.now(singapore_tz)
    date_string = today.strftime("%Y-%m-%d")
    
    print(f"   📆 Clearing events for: {date_string}")
    
    # Delete all events for today
    result = await delete_events_by_date(user_id, date_string)
    
    # Goofy rest messages
    goofy_messages = [
        "🛋️ <b>YEET! All your plans have been yeeted into the void!</b>\n\n"
        "Go touch some grass, you deserve it. 🌱\n\n"
        "Maybe take a nap? Or seven? 😴\n\n"
        "<i>Your calendar is now as empty as my motivation on a Monday.</i>",
        
        "🎉 <b>POOF! Your schedule went *brrrrr* and disappeared!</b>\n\n"
        "Time to become one with the couch. 🛋️\n\n"
        "Netflix isn't gonna watch itself, you know. 📺\n\n"
        "<i>Productivity? Never heard of her.</i>",
        
        "✨ <b>*waves magic wand* ABRACADABRA! Events begone!</b>\n\n"
        "Your only task now is to REST. That's an order! 🫡\n\n"
        "Go hydrate. Eat a snack. Pet a dog. 🐕\n\n"
        "<i>You're officially on vacation (self-declared).</i>",
        
        "🚀 <b>Houston, we have liftoff! Your events have left the planet!</b>\n\n"
        "Time to activate ultra-relaxation mode. 😎\n\n"
        "Warning: May cause extreme comfort and happiness.\n\n"
        "<i>Side effects include: smiling, breathing deeply, and actually enjoying life.</i>",
        
        "💥 <b>KABOOM! Your to-do list has exploded into confetti!</b>\n\n"
        "🎊 Congratulations! You've unlocked: FREE TIME! 🎊\n\n"
        "Quick, do nothing before responsibilities find you! 🏃‍♂️\n\n"
        "<i>Remember: You can't be late if you have nowhere to be *taps head*</i>",
    ]
    
    # Pick a random goofy message
    goofy_message = random.choice(goofy_messages)
    
    if result.get("status") == "success":
        deleted_count = result.get("count", 0)
        
        if deleted_count == 0:
            # No events to delete
            message = """
🤷 <b>Ummm... there's nothing to clear!</b>

Your schedule was already empty. You absolute legend. 👑

You were ALREADY resting and didn't even know it!

<i>Go ahead, continue being a professional relaxation expert.</i>
            """.strip()
        else:
            # Events were deleted - show goofy message
            message = f"🗑️ <i>Cleared {deleted_count} event{'s' if deleted_count != 1 else ''}...</i>\n\n{goofy_message}"
        
        await send_message(user_id, message)
        print(f"   ✅ Cleared {deleted_count} events and sent goofy rest message")
        
    else:
        # Error occurred
        error_msg = f"""
❌ <b>Oops! Something went wrong!</b>

Could not clear your events.

<b>Error:</b> {result.get('message', 'Unknown error')}

Please try again later. (Or maybe it's a sign you shouldn't rest? Nah, definitely try again.)
        """.strip()
        
        await send_message(user_id, error_msg)
        print(f"   ❌ Failed to clear events: {result.get('message')}")


# ============================================================================
# PHASE 7: NIGHTLY BRIEFING - /force_briefing Command (Demo)
# ============================================================================

async def handle_force_briefing(user_id: int):
    """
    Phase 7: Force Briefing Command (Demo/Testing)
    
    This is a hidden command to demonstrate the nightly briefing feature
    during hackathon demos without waiting for 9 PM.
    
    Usage: Send "/force_briefing" to the bot in private chat
    
    Args:
        user_id: The user's Telegram ID
    """
    from app.bot.briefing import force_send_briefing
    
    print(f"\n🎯 DEMO: Force briefing for User {user_id}")
    
    # Send a confirmation that we're processing
    loading_msg = "🌙 <b>Generating your briefing...</b>\n\n<i>Fetching tomorrow's schedule...</i>"
    response = await send_message(user_id, loading_msg)
    
    # Get message_id for potential editing
    message_id = response.get("result", {}).get("message_id") if response.get("ok") else None
    
    # Call the force briefing function
    result = await force_send_briefing(user_id)
    
    if result.get("status") == "success":
        print(f"   ✅ Force briefing sent ({result.get('event_count')} events)")
    else:
        print(f"   ❌ Force briefing failed: {result.get('message')}")
        
        # Send error message
        error_msg = f"""
❌ <b>Briefing Failed</b>

{result.get('message', 'Unknown error')}

Please try again later.
        """.strip()
        await send_message(user_id, error_msg)


# ============================================================================
# PHASE 6: ACTIVE RESEARCH MODE - /track Command
# ============================================================================

async def handle_track_command(text: str, user_id: int):
    """
    Phase 6: Active Research Mode - The /track Command Handler
    
    Flow:
    1. Extract topic from command (e.g., "/track CS2103 deadlines" → "CS2103 deadlines")
    2. Send loading message (Async UI pattern)
    3. Call Member A's scavenge_events(topic) to search the web
    4. If no events found → Edit message with "no results" notification
    5. If events found → Save to DB and edit message with formatted event card
    
    Args:
        text: The full command text (e.g., "/track CS2103 deadlines")
        user_id: The user's Telegram ID
    """
    print(f"\n🕵️ TRACK: Processing research request from User {user_id}")
    
    # ========================================================================
    # STEP 1: Extract topic from command
    # ========================================================================
    # Remove "/track" prefix and get the topic
    # Handle both "/track topic" and "/track  topic" (multiple spaces)
    topic = text[6:].strip()  # Remove "/track" (6 characters)
    
    if not topic:
        # No topic provided - send helpful error message
        error_msg = """
❌ <b>Missing Topic</b>

Please provide a topic to research!

<b>Examples:</b>
• /track CS2103 deadlines
• /track NUS academic calendar
• /track Singapore public holidays
        """.strip()
        await send_message(user_id, error_msg)
        print("   ⚠️ No topic provided")
        return
    
    print(f"   📋 Topic: '{topic}'")
    
    # ========================================================================
    # STEP 2: Send loading message (Async UI pattern)
    # ========================================================================
    loading_msg = f"""
🕵️ <b>Activating Research Agent...</b>

🔍 Searching for '<b>{topic}</b>'...

<i>This may take a few seconds...</i>
    """.strip()
    
    response = await send_message(user_id, loading_msg)
    
    if not response.get("ok"):
        print(f"   ❌ Failed to send loading message: {response.get('error')}")
        return
    
    # Capture message_id for editing later
    message_id = response.get("result", {}).get("message_id")
    if not message_id:
        print("   ❌ No message_id received from Telegram")
        return
    
    print(f"   📤 Loading message sent (message_id: {message_id})")
    
    # ========================================================================
    # STEP 3: Call Member A's scavenge_events function
    # ========================================================================
    try:
        events: List[Event] = await scavenge_events(topic)
        print(f"   🔍 Scavenge returned {len(events)} events")
    except Exception as e:
        print(f"   ❌ Scavenge error: {e}")
        error_msg = f"""
❌ <b>Research Failed</b>

Could not search for '<b>{topic}</b>'.

<b>Error:</b> {str(e)}

Please try again later.
        """.strip()
        await edit_message(user_id, message_id, error_msg)
        return
    
    # ========================================================================
    # STEP 4: Handle empty results
    # ========================================================================
    if not events:
        no_results_msg = f"""
🔍 <b>No Events Found</b>

Could not find specific dates or deadlines for '<b>{topic}</b>'.

<b>Try:</b>
• Being more specific (e.g., "CS2103 2026 deadlines")
• Using official names (e.g., "NUS Academic Calendar")
• Checking for typos
        """.strip()
        await edit_message(user_id, message_id, no_results_msg)
        print("   📭 No events found for topic")
        return
    
    # ========================================================================
    # STEP 5: Save events to database
    # ========================================================================
    save_result = await save_scavenged_events_batch(events, user_id)
    
    if save_result.get("status") == "error":
        error_msg = f"""
❌ <b>Failed to Save Events</b>

Found {len(events)} events for '<b>{topic}</b>' but could not save them.

<b>Error:</b> {save_result.get('message', 'Unknown error')}

Please try again later.
        """.strip()
        await edit_message(user_id, message_id, error_msg)
        print(f"   ❌ Failed to save events: {save_result.get('message')}")
        return
    
    saved_count = save_result.get("count", len(events))
    print(f"   ✅ Saved {saved_count} events to database")
    
    # ========================================================================
    # STEP 6: Format and display the results card
    # ========================================================================
    result_msg = format_scavenged_events_card(events, topic)
    
    # Edit the loading message with the final result
    edit_result = await edit_message(user_id, message_id, result_msg)
    
    if edit_result.get("ok"):
        print(f"   ✅ Research complete! Displayed {len(events)} events to user")
    else:
        print(f"   ❌ Failed to edit message: {edit_result.get('error')}")
        # Fallback: Send as new message
        await send_message(user_id, result_msg)


def format_scavenged_events_card(events: List[Event], topic: str) -> str:
    """
    Format a list of scavenged events into a single consolidated card.
    
    Design Spec:
    - Header: Shows topic and count
    - Body: List of events with title and formatted date
    - Footer: Success confirmation
    - Limit: Show max 10 events, then "...and X more"
    
    Args:
        events: List of Event Pydantic models from scavenge_events()
        topic: The original search topic for display
        
    Returns:
        HTML-formatted string for Telegram
    """
    from app.bot.responses import sanitize_html
    
    total_count = len(events)
    display_count = min(total_count, 10)  # Cap at 10 events
    
    # ========================================================================
    # HEADER
    # ========================================================================
    safe_topic = sanitize_html(topic)
    card = f"🔍 <b>Research Complete: {safe_topic}</b>\n\n"
    card += f"📋 Found <b>{total_count}</b> event{'s' if total_count != 1 else ''}:\n\n"
    
    # ========================================================================
    # EVENT LIST (max 10)
    # ========================================================================
    for idx, event in enumerate(events[:display_count], 1):
        # Format the title
        title = sanitize_html(event.title) if event.title else "Untitled Event"
        
        # Format the date/time
        formatted_time = format_datetime(event.start_time) if event.start_time else "Date TBD"
        
        # Build event line with numbering
        card += f"<b>{idx}.</b> {title}\n"
        card += f"   📅 {formatted_time}\n"
        
        # Add location if available
        if event.location:
            location = sanitize_html(event.location)
            card += f"   📍 {location}\n"
        
        card += "\n"  # Spacing between events
    
    # ========================================================================
    # "AND X MORE" INDICATOR (if more than 10 events)
    # ========================================================================
    if total_count > 10:
        remaining = total_count - 10
        card += f"<i>...and {remaining} more event{'s' if remaining != 1 else ''}.</i>\n\n"
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    card += "✅ <b>Added to your calendar!</b>\n"
    card += f"🌐 <i>Source: Web Research</i>"
    
    return card.strip()
