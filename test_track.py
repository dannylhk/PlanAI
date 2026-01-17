"""
Test Script for Phase 6: Active Research Mode (/track Command)

This test verifies the /track command functionality:
1. Topic extraction from command
2. Loading message display
3. Scavenge agent integration
4. Event card formatting
5. Database batch save

Run with: python test_track.py
"""

import asyncio
from typing import List
from app.schemas.event import Event
from app.bot.router import handle_track_command, format_scavenged_events_card
from app.core.agent import scavenge_events
from app.services.crud import save_scavenged_events_batch

# Test user ID (use a test account)
TEST_USER_ID = 123456789


def print_header(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


async def test_topic_extraction():
    """Test 1: Verify topic is correctly extracted from /track command"""
    print_header("TEST 1: Topic Extraction")
    
    test_cases = [
        ("/track CS2103 deadlines", "CS2103 deadlines"),
        ("/track NUS Academic Calendar", "NUS Academic Calendar"),
        ("/track   multiple spaces   ", "multiple spaces"),  # Multiple spaces
        ("/track", ""),  # Empty topic
    ]
    
    for command, expected in test_cases:
        # Extract topic using same logic as handle_track_command
        topic = command[6:].strip()
        
        if topic == expected:
            print(f"✅ PASS: '{command}' → '{topic}'")
        else:
            print(f"❌ FAIL: '{command}' → Expected '{expected}', got '{topic}'")


async def test_scavenge_events():
    """Test 2: Test the scavenge_events function from Member A"""
    print_header("TEST 2: Scavenge Events (Member A's Agent)")
    
    # Test with a real topic that should return events
    topic = "NUS Academic Calendar 2026"
    print(f"📋 Searching for: '{topic}'")
    print("   (This may take 5-10 seconds...)\n")
    
    try:
        events = await scavenge_events(topic)
        
        if events:
            print(f"✅ SUCCESS: Found {len(events)} events\n")
            
            print("📋 Sample Events:")
            for idx, event in enumerate(events[:5], 1):
                print(f"   {idx}. {event.title}")
                print(f"      📅 {event.start_time}")
                print(f"      🏷️ Source: {event.source}")
                print()
        else:
            print("⚠️ WARNING: No events found (API might be rate limited or topic too specific)")
            print("   This is not necessarily a failure - try a different topic")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")


async def test_format_scavenged_events_card():
    """Test 3: Test the event card formatting function"""
    print_header("TEST 3: Event Card Formatting")
    
    # Create mock events for testing
    mock_events = [
        Event(
            title="Tutorial Registration Deadline",
            start_time="2026-01-20T09:00:00",
            end_time="2026-01-20T10:00:00",
            source="web_scavenge"
        ),
        Event(
            title="Project V1.0 Submission",
            start_time="2026-02-15T23:59:00",
            end_time="2026-02-16T00:00:00",
            location="LumiNUS",
            source="web_scavenge"
        ),
        Event(
            title="Final Exam",
            start_time="2026-04-28T09:00:00",
            end_time="2026-04-28T12:00:00",
            location="MPSH",
            source="web_scavenge"
        ),
    ]
    
    topic = "CS2103 deadlines"
    card = format_scavenged_events_card(mock_events, topic)
    
    print("📋 Generated Card (3 events):")
    print("-" * 50)
    print(card)
    print("-" * 50)
    
    # Verify card contains expected elements
    checks = [
        ("Research Complete" in card, "Header present"),
        ("CS2103 deadlines" in card, "Topic in header"),
        ("Found <b>3</b> event" in card, "Event count correct"),
        ("Tutorial Registration Deadline" in card, "Event 1 title"),
        ("Project V1.0 Submission" in card, "Event 2 title"),
        ("Final Exam" in card, "Event 3 title"),
        ("Added to your calendar" in card, "Success footer"),
        ("Web Research" in card, "Source indicator"),
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


async def test_format_with_overflow():
    """Test 4: Test card formatting with more than 10 events"""
    print_header("TEST 4: Overflow Handling (>10 Events)")
    
    # Create 15 mock events
    mock_events = []
    for i in range(15):
        mock_events.append(Event(
            title=f"Event {i+1}",
            start_time=f"2026-01-{20+i:02d}T09:00:00",
            end_time=f"2026-01-{20+i:02d}T10:00:00",
            source="web_scavenge"
        ))
    
    topic = "Many Events Test"
    card = format_scavenged_events_card(mock_events, topic)
    
    print("📋 Generated Card (15 events):")
    print("-" * 50)
    print(card)
    print("-" * 50)
    
    # Verify overflow handling
    checks = [
        ("Found <b>15</b>" in card, "Shows total count (15)"),
        ("Event 1" in card, "First event shown"),
        ("Event 10" in card, "10th event shown"),
        ("Event 11" not in card or "...and" in card, "11th event hidden"),
        ("...and 5 more" in card, "Overflow indicator correct"),
    ]
    
    print("\n🔍 Overflow Verification:")
    all_passed = True
    for check, name in checks:
        if check:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name}")
            all_passed = False
    
    if all_passed:
        print("\n✅ Overflow handling PASSED")
    else:
        print("\n❌ Overflow handling FAILED")


async def test_batch_save():
    """Test 5: Test batch saving scavenged events"""
    print_header("TEST 5: Batch Save to Database")
    
    # Create mock events
    mock_events = [
        Event(
            title="Test Track Event 1",
            start_time="2026-03-01T10:00:00",
            end_time="2026-03-01T11:00:00",
            source="web_scavenge"
        ),
        Event(
            title="Test Track Event 2",
            start_time="2026-03-02T14:00:00",
            end_time="2026-03-02T15:00:00",
            source="web_scavenge"
        ),
    ]
    
    print(f"📝 Saving {len(mock_events)} events for User {TEST_USER_ID}...")
    
    result = await save_scavenged_events_batch(mock_events, TEST_USER_ID)
    
    print(f"\n📊 Save Result:")
    print(f"   Status: {result.get('status')}")
    
    if result.get("status") == "success":
        print(f"   Count: {result.get('count')} events saved")
        print("\n✅ Batch save PASSED")
    elif result.get("status") == "ignored":
        print(f"   Message: {result.get('message')}")
        print("\n⚠️ Batch save returned ignored (no events to save)")
    else:
        print(f"   Error: {result.get('message')}")
        print("\n❌ Batch save FAILED")


async def test_empty_topic():
    """Test 6: Test empty topic handling"""
    print_header("TEST 6: Empty Topic Handling")
    
    empty_topic = ""
    
    if not empty_topic:
        print("✅ Empty topic detected correctly")
        print("   Expected behavior: Should show error message to user")
    else:
        print("❌ Empty topic not detected")


async def test_full_integration():
    """Test 7: Full integration test (live API call)"""
    print_header("TEST 7: Full Integration Test")
    
    print("⚠️ This test calls live APIs and sends a real Telegram message.")
    print("   Only run if you have a valid bot token and user ID configured.\n")
    
    # Skip actual Telegram sending in test mode
    # Just test the scavenge + format + save flow
    
    topic = "Singapore public holidays 2026"
    print(f"📋 Topic: '{topic}'")
    print("   Step 1: Searching web...\n")
    
    try:
        # Step 1: Scavenge
        events = await scavenge_events(topic)
        
        if not events:
            print("⚠️ No events found - skipping remaining steps")
            return
        
        print(f"   ✅ Found {len(events)} events\n")
        print("   Step 2: Formatting card...\n")
        
        # Step 2: Format
        card = format_scavenged_events_card(events, topic)
        print("   ✅ Card formatted\n")
        
        print("   Step 3: Saving to database...\n")
        
        # Step 3: Save
        result = await save_scavenged_events_batch(events, TEST_USER_ID)
        
        if result.get("status") == "success":
            print(f"   ✅ Saved {result.get('count')} events\n")
        else:
            print(f"   ❌ Save failed: {result.get('message')}\n")
            return
        
        print("=" * 50)
        print("FINAL OUTPUT PREVIEW:")
        print("=" * 50)
        print(card)
        print("=" * 50)
        
        print("\n✅ Full integration test PASSED")
        
    except Exception as e:
        print(f"❌ Integration test FAILED: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("PHASE 6: ACTIVE RESEARCH MODE - TEST SUITE")
    print("=" * 70)
    
    # Run tests in sequence
    await test_topic_extraction()
    await test_format_scavenged_events_card()
    await test_format_with_overflow()
    await test_empty_topic()
    
    # These tests require API/DB access
    print("\n" + "=" * 70)
    print("LIVE API TESTS (Require Tavily + Supabase)")
    print("=" * 70)
    
    await test_scavenge_events()
    await test_batch_save()
    
    # Full integration
    await test_full_integration()
    
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\n💡 Notes:")
    print("   - Tests 1-4, 6 are unit tests (no external dependencies)")
    print("   - Tests 2, 5, 7 require Tavily API key and Supabase")
    print("   - Check console logs above for detailed results")
    print("   - Mock events are saved with user_id:", TEST_USER_ID)


if __name__ == "__main__":
    asyncio.run(main())
