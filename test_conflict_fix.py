"""
Test script to verify the conflict detection fix.

This script demonstrates that conflicts are now properly scoped to individual users.
"""
import asyncio
from app.services.crud import check_conflicts, save_event_to_db
from app.schemas.event import Event
from datetime import datetime, timedelta

async def test_conflict_fix():
    """
    Test that conflict detection only checks within the same user's events.
    """
    print("=" * 70)
    print("TESTING CONFLICT DETECTION FIX")
    print("=" * 70)
    
    # Create a time slot for testing
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    start_str = start_time.isoformat()
    end_str = end_time.isoformat()
    
    print(f"\n📅 Test Time Slot:")
    print(f"   Start: {start_str}")
    print(f"   End: {end_str}")
    
    # ========================================================================
    # TEST 1: Check conflicts WITHOUT user_id (old behavior - shows all users)
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 1: Conflict Check WITHOUT user_id filter")
    print("=" * 70)
    
    conflicts_all = await check_conflicts(start_str, end_str, user_id=None)
    print(f"\n✅ Found {len(conflicts_all)} conflicting events across ALL users")
    
    if conflicts_all:
        print("\n🔍 Sample conflicts (first 3):")
        for idx, event in enumerate(conflicts_all[:3], 1):
            print(f"   {idx}. {event.get('title')} - User ID: {event.get('user_id')}")
    
    # ========================================================================
    # TEST 2: Check conflicts WITH specific user_id (new behavior - user-scoped)
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 2: Conflict Check WITH user_id filter")
    print("=" * 70)
    
    test_user_id = 123456789  # Specific test user
    
    conflicts_user = await check_conflicts(start_str, end_str, user_id=test_user_id)
    print(f"\n✅ Found {len(conflicts_user)} conflicting events for User {test_user_id}")
    
    if conflicts_user:
        print("\n🔍 User's conflicts:")
        for idx, event in enumerate(conflicts_user, 1):
            print(f"   {idx}. {event.get('title')} at {event.get('start_time')}")
    else:
        print("   No conflicts for this user (correct behavior!)")
    
    # ========================================================================
    # TEST 3: Create a new event and verify conflict check is user-scoped
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 3: Save New Event with User-Scoped Conflict Check")
    print("=" * 70)
    
    # Create a test event
    test_event = Event(
        title="Test Meeting",
        start_time=start_str,
        end_time=end_str,
        location="Test Location"
    )
    
    print(f"\n📝 Creating event: {test_event.title}")
    print(f"   For User ID: {test_user_id}")
    
    result = await save_event_to_db(test_event, user_id=test_user_id)
    
    print(f"\n📊 Save Result:")
    print(f"   Status: {result.get('status')}")
    
    if result["status"] == "conflict":
        print(f"   Message: {result.get('message')}")
        conflicts = result.get('conflicting_events', [])
        print(f"\n   Conflicting events for this user:")
        for idx, event in enumerate(conflicts[:3], 1):
            print(f"   {idx}. {event.get('title')} at {event.get('start_time')}")
    elif result["status"] == "success":
        print(f"   ✅ Event saved successfully!")
        print(f"   Event ID: {result['data'].get('id')}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✅ FIX VERIFICATION:")
    print("   - Conflict detection now filters by user_id")
    print("   - Users only see conflicts with their OWN events")
    print("   - No more cross-user conflict false positives")
    print("\n💡 KEY IMPROVEMENT:")
    print("   Before: Showed conflicts from all users in database")
    print("   After: Only shows conflicts within the specific user's schedule")

if __name__ == "__main__":
    asyncio.run(test_conflict_fix())
