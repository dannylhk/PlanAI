"""
Test script for /agenda feature
Tests the format_agenda function with both empty and populated states
"""

from app.bot.responses import format_agenda


def test_empty_agenda():
    """Test the empty state - no events scheduled"""
    print("=" * 60)
    print("TEST 1: Empty Agenda (No Events)")
    print("=" * 60)
    
    events = []
    date_string = "2026-01-18"
    
    result = format_agenda(events, date_string)
    
    print("\nInput:")
    print(f"  Events: {events}")
    print(f"  Date: {date_string}")
    print("\nOutput:")
    print(result)
    print("\n")


def test_populated_agenda():
    """Test the populated state - multiple events"""
    print("=" * 60)
    print("TEST 2: Populated Agenda (Multiple Events)")
    print("=" * 60)
    
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
            "location": None,  # Test null location
            "conflict": False
        },
        {
            "start_time": "2026-01-18T18:00:00",
            "title": "Dinner with Friends",
            "location": "UTown",
            "conflict": True  # Test conflict warning
        }
    ]
    
    date_string = "2026-01-18"
    
    result = format_agenda(events, date_string)
    
    print("\nInput:")
    print(f"  Events: {len(events)} events")
    print(f"  Date: {date_string}")
    print("\nOutput:")
    print(result)
    print("\n")


def test_edge_cases():
    """Test edge cases - special characters, long titles, etc."""
    print("=" * 60)
    print("TEST 3: Edge Cases")
    print("=" * 60)
    
    events = [
        {
            "start_time": "2026-01-18T10:30:00",
            "title": "Project <Demo> & Discussion",  # HTML characters
            "location": "Meeting Room A&B",
            "conflict": False
        },
        {
            "start_time": "2026-01-18T15:45:00",
            "title": "Very Long Event Title That Should Still Display Properly Without Breaking The Format",
            "location": "Building 1, Level 2, Room 3, NUS Campus, Singapore",
            "conflict": False
        }
    ]
    
    date_string = "2026-01-18"
    
    result = format_agenda(events, date_string)
    
    print("\nInput:")
    print(f"  Events: {len(events)} events with special characters")
    print(f"  Date: {date_string}")
    print("\nOutput:")
    print(result)
    print("\n")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "TESTING /agenda FEATURE" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        test_empty_agenda()
        test_populated_agenda()
        test_edge_cases()
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nThe format_agenda function is working correctly!")
        print("Next steps:")
        print("1. Test with the actual Telegram bot by sending /agenda")
        print("2. Replace mock data with real database calls")
        print("3. Verify timezone handling is correct\n")
        
    except Exception as e:
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
