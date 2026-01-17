"""
Test Script for Phase 7: Nightly Briefing

This test verifies the nightly briefing functionality:
1. Briefing message formatting
2. Tomorrow's date calculation
3. User event retrieval
4. Force briefing command

Run with: python test_briefing.py
"""

import asyncio
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any

from app.bot.briefing import (
    send_nightly_briefing, 
    format_briefing_message, 
    force_send_briefing
)
from app.services.crud import get_users_with_events_for_date, get_events_by_date

# Test user ID
TEST_USER_ID = 123456789


def print_header(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


async def test_date_calculation():
    """Test 1: Verify tomorrow's date calculation in Singapore timezone"""
    print_header("TEST 1: Tomorrow's Date Calculation")
    
    singapore_tz = pytz.timezone('Asia/Singapore')
    now = datetime.now(singapore_tz)
    tomorrow = now + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    print(f"📅 Current time (SGT): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Tomorrow's date: {tomorrow_str}")
    print(f"📅 Formatted: {tomorrow.strftime('%A, %B %d, %Y')}")
    
    # Verify format
    if len(tomorrow_str) == 10 and tomorrow_str[4] == '-' and tomorrow_str[7] == '-':
        print("\n✅ Date format correct (YYYY-MM-DD)")
    else:
        print("\n❌ Date format incorrect")


async def test_format_briefing_message():
    """Test 2: Test the briefing message formatting"""
    print_header("TEST 2: Briefing Message Formatting")
    
    # Create mock events
    mock_events = [
        {
            "title": "Morning Meeting",
            "start_time": "2026-01-19T09:00:00",
            "location": "Conference Room A"
        },
        {
            "title": "Lunch with Team",
            "start_time": "2026-01-19T12:00:00",
            "location": "Deck Canteen"
        },
        {
            "title": "Project Review",
            "start_time": "2026-01-19T15:00:00",
            "location": None  # Test null location
        }
    ]
    
    # Get tomorrow's date
    singapore_tz = pytz.timezone('Asia/Singapore')
    tomorrow = datetime.now(singapore_tz) + timedelta(days=1)
    
    # Format the message
    message = format_briefing_message(mock_events, tomorrow)
    
    print("📋 Generated Briefing Message:")
    print("-" * 50)
    print(message)
    print("-" * 50)
    
    # Verify message contains expected elements
    checks = [
        ("Tomorrow's Schedule" in message, "Header present"),
        ("3" in message, "Event count shown"),
        ("Morning Meeting" in message, "Event 1 title"),
        ("Lunch with Team" in message, "Event 2 title"),
        ("Project Review" in message, "Event 3 title"),
        ("09:00" in message, "Time formatting"),
        ("Conference Room A" in message, "Location shown"),
        ("Have a great day" in message or "productive" in message, "Footer message"),
    ]
    
    print("\n🔍 Verification:")
    all_passed = True
    for check, name in checks:
        if check:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name}")
            all_passed = False
    
    if all_passed:
        print("\n✅ All format checks PASSED")
    else:
        print("\n❌ Some format checks FAILED")


async def test_format_with_many_events():
    """Test 3: Test formatting with 5+ events (busy day message)"""
    print_header("TEST 3: Busy Day Formatting (5+ Events)")
    
    # Create 6 mock events
    mock_events = []
    for i in range(6):
        mock_events.append({
            "title": f"Event {i+1}",
            "start_time": f"2026-01-19T{9+i:02d}:00:00",
            "location": f"Room {i+1}"
        })
    
    singapore_tz = pytz.timezone('Asia/Singapore')
    tomorrow = datetime.now(singapore_tz) + timedelta(days=1)
    
    message = format_briefing_message(mock_events, tomorrow)
    
    print("📋 Generated Briefing Message (6 events):")
    print("-" * 50)
    print(message)
    print("-" * 50)
    
    # Check for busy day message
    if "Busy day ahead" in message:
        print("\n✅ Busy day footer detected (correct for 5+ events)")
    else:
        print("\n⚠️ Busy day footer not found")


async def test_get_users_with_events():
    """Test 4: Test fetching users with events for tomorrow"""
    print_header("TEST 4: Get Users with Events for Tomorrow")
    
    singapore_tz = pytz.timezone('Asia/Singapore')
    tomorrow = datetime.now(singapore_tz) + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    print(f"📅 Checking for users with events on: {tomorrow_str}")
    
    try:
        user_ids = await get_users_with_events_for_date(tomorrow_str)
        
        if user_ids:
            print(f"\n✅ Found {len(user_ids)} user(s) with events tomorrow:")
            for uid in user_ids[:5]:  # Show first 5
                print(f"   - User ID: {uid}")
            if len(user_ids) > 5:
                print(f"   ... and {len(user_ids) - 5} more")
        else:
            print("\n📭 No users have events tomorrow")
            print("   (This is expected if no test events were added for tomorrow)")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def test_get_events_for_user():
    """Test 5: Test fetching events for a specific user"""
    print_header("TEST 5: Get Events for Test User")
    
    singapore_tz = pytz.timezone('Asia/Singapore')
    tomorrow = datetime.now(singapore_tz) + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    print(f"📅 Fetching events for User {TEST_USER_ID} on: {tomorrow_str}")
    
    try:
        events = await get_events_by_date(TEST_USER_ID, tomorrow_str)
        
        if events:
            print(f"\n✅ Found {len(events)} event(s):")
            for idx, event in enumerate(events[:5], 1):
                print(f"   {idx}. {event.get('title')} at {event.get('start_time')}")
        else:
            print("\n📭 No events found for this user tomorrow")
            print("   (Add events for tomorrow to test the full flow)")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def test_force_briefing():
    """Test 6: Test force briefing command (Live Telegram call)"""
    print_header("TEST 6: Force Briefing (Live Test)")
    
    print("⚠️ This test sends a real Telegram message!")
    print(f"   Target User ID: {TEST_USER_ID}")
    print("\n🌙 Sending force briefing...")
    
    try:
        result = await force_send_briefing(TEST_USER_ID)
        
        print(f"\n📊 Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Event Count: {result.get('event_count')}")
        print(f"   Message: {result.get('message')}")
        
        if result.get("status") == "success":
            print("\n✅ Force briefing PASSED")
        else:
            print("\n⚠️ Force briefing completed with issues")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def test_full_nightly_briefing():
    """Test 7: Test the full nightly briefing job (without sending)"""
    print_header("TEST 7: Full Nightly Briefing Flow (Dry Run)")
    
    print("📋 This tests the full nightly briefing flow:")
    print("   1. Calculate tomorrow's date")
    print("   2. Find all users with events")
    print("   3. Prepare briefings for each user")
    print("\n⚠️ Note: This will send real messages if users have events!")
    print("   Running in 3 seconds...")
    
    await asyncio.sleep(3)
    
    try:
        await send_nightly_briefing()
        print("\n✅ Nightly briefing job completed")
    except Exception as e:
        print(f"\n❌ Error during briefing: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("PHASE 7: NIGHTLY BRIEFING - TEST SUITE")
    print("=" * 70)
    
    # Unit tests (no external dependencies)
    await test_date_calculation()
    await test_format_briefing_message()
    await test_format_with_many_events()
    
    # Database tests
    print("\n" + "=" * 70)
    print("DATABASE TESTS (Require Supabase)")
    print("=" * 70)
    
    await test_get_users_with_events()
    await test_get_events_for_user()
    
    # Live test
    print("\n" + "=" * 70)
    print("LIVE TESTS (Require Telegram Bot)")
    print("=" * 70)
    
    await test_force_briefing()
    
    # Full flow (optional - comment out if not needed)
    # await test_full_nightly_briefing()
    
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\n💡 How to use /force_briefing command:")
    print("   1. Open your Telegram bot in private chat")
    print("   2. Send: /force_briefing")
    print("   3. Bot will send you tomorrow's schedule immediately")
    print("   4. Use this during demo to show the 9 PM briefing feature!")
    print("\n💡 Scheduler Status:")
    print("   Visit http://localhost:8000/scheduler/status to check")
    print("   the next scheduled briefing time.")


if __name__ == "__main__":
    asyncio.run(main())
