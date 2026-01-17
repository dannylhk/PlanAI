"""
Nightly Briefing Module - Phase 7
Sends push notifications at 9 PM with tomorrow's schedule
"""
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any

from app.bot.responses import send_message, sanitize_html
from app.bot.date_utils import format_datetime
from app.services.crud import get_users_with_events_for_date, get_events_by_date


async def send_nightly_briefing():
    """
    Phase 7: The Nightly Briefing Job
    
    This function is called by APScheduler at 9 PM Singapore time.
    It sends tomorrow's schedule to all users who have events.
    
    Flow:
    1. Calculate tomorrow's date (Singapore timezone)
    2. Get all user_ids with events tomorrow
    3. For each user, get their events and send a briefing
    
    Called by: APScheduler cron job (9 PM daily)
    """
    print("\n" + "=" * 60)
    print("🌙 NIGHTLY BRIEFING - Starting at 9 PM SGT")
    print("=" * 60)
    
    # Step 1: Calculate tomorrow's date in Singapore timezone
    singapore_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(singapore_tz)
    tomorrow = now + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    print(f"📅 Preparing briefings for: {tomorrow.strftime('%A, %B %d, %Y')}")
    
    # Step 2: Get all users with events tomorrow
    user_ids = await get_users_with_events_for_date(tomorrow_str)
    
    if not user_ids:
        print("📭 No users have events tomorrow. Briefing complete.")
        print("=" * 60 + "\n")
        return
    
    print(f"👥 Found {len(user_ids)} user(s) with events tomorrow")
    
    # Step 3: Send briefing to each user
    success_count = 0
    fail_count = 0
    
    for user_id in user_ids:
        try:
            # Get user's events for tomorrow
            events = await get_events_by_date(user_id, tomorrow_str)
            
            if events:
                # Format and send the briefing
                message = format_briefing_message(events, tomorrow)
                result = await send_message(user_id, message)
                
                if result.get("ok"):
                    print(f"   ✅ Sent briefing to User {user_id} ({len(events)} events)")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to send to User {user_id}: {result.get('error')}")
                    fail_count += 1
            else:
                print(f"   ⏭️  User {user_id} - No events found (skipped)")
                
        except Exception as e:
            print(f"   ❌ Error processing User {user_id}: {e}")
            fail_count += 1
    
    # Summary
    print(f"\n📊 Briefing Summary: {success_count} sent, {fail_count} failed")
    print("=" * 60 + "\n")


def format_briefing_message(events: List[Dict[str, Any]], date: datetime) -> str:
    """
    Format the nightly briefing message with tomorrow's events.
    
    Design:
    - Header: "🌙 Tomorrow's Schedule"
    - Date: "Saturday, January 18, 2026"
    - Event list: Time + Title + Location
    - Footer: Motivational message
    
    Args:
        events: List of event dictionaries from database
        date: The date for the briefing (tomorrow)
        
    Returns:
        HTML-formatted string for Telegram
    """
    # Header
    formatted_date = date.strftime("%A, %B %d, %Y")
    message = f"🌙 <b>Tomorrow's Schedule</b>\n"
    message += f"📅 {formatted_date}\n\n"
    
    # Count events
    event_count = len(events)
    message += f"You have <b>{event_count}</b> event{'s' if event_count != 1 else ''} tomorrow:\n\n"
    
    # Event list
    for idx, event in enumerate(events, 1):
        title = sanitize_html(event.get("title", "Untitled Event"))
        start_time_raw = event.get("start_time", "")
        location = event.get("location")
        
        # Format time (extract just HH:MM)
        try:
            if "T" in start_time_raw:
                time_part = start_time_raw.split("T")[1][:5]  # Get "HH:MM"
            else:
                time_part = "TBD"
        except:
            time_part = "TBD"
        
        # Build event line
        message += f"<b>{time_part}</b> - {title}\n"
        
        if location:
            location_clean = sanitize_html(location)
            message += f"   📍 <i>{location_clean}</i>\n"
        
        message += "\n"
    
    # Footer - Motivational message based on event count
    if event_count >= 5:
        message += "💪 <i>Busy day ahead! You've got this!</i>"
    elif event_count >= 3:
        message += "✨ <i>Have a productive day tomorrow!</i>"
    else:
        message += "🌟 <i>Have a great day tomorrow!</i>"
    
    return message.strip()


async def force_send_briefing(user_id: int) -> Dict[str, Any]:
    """
    Force send a briefing to a specific user (for demo purposes).
    
    This is called by the /force_briefing command to demonstrate
    the nightly briefing feature without waiting for 9 PM.
    
    Args:
        user_id: The user's Telegram ID
        
    Returns:
        Dict with status and message
    """
    print(f"\n🎯 FORCE BRIEFING triggered for User {user_id}")
    
    # Get tomorrow's date
    singapore_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(singapore_tz)
    tomorrow = now + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    print(f"   📅 Getting events for: {tomorrow_str}")
    
    # Get user's events for tomorrow
    events = await get_events_by_date(user_id, tomorrow_str)
    
    if not events:
        # No events - send a different message
        no_events_msg = f"""
🌙 <b>Tomorrow's Schedule</b>
📅 {tomorrow.strftime("%A, %B %d, %Y")}

🎉 <b>No events scheduled!</b>

<i>Enjoy your free time tomorrow! Use /track to research upcoming deadlines.</i>
        """.strip()
        
        result = await send_message(user_id, no_events_msg)
        
        return {
            "status": "success" if result.get("ok") else "error",
            "event_count": 0,
            "message": "No events for tomorrow"
        }
    
    # Format and send the briefing
    message = format_briefing_message(events, tomorrow)
    result = await send_message(user_id, message)
    
    if result.get("ok"):
        print(f"   ✅ Force briefing sent successfully ({len(events)} events)")
        return {
            "status": "success",
            "event_count": len(events),
            "message": f"Briefing sent with {len(events)} events"
        }
    else:
        print(f"   ❌ Failed to send: {result.get('error')}")
        return {
            "status": "error",
            "event_count": len(events),
            "message": result.get("error", "Unknown error")
        }
