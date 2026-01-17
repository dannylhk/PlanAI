"""
Test script for Phase 5: Statefulness (Short-Term Memory)

This script tests the chat_context memory system and update detection.
"""
import asyncio
from app.bot.router import handle_group_listener, chat_context
from app.services.crud import save_event_to_db
from app.schemas.event import Event
from datetime import datetime, timedelta

async def test_statefulness():
    """
    Test the statefulness flow:
    1. Create an initial event
    2. Try to update it with a follow-up message
    3. Verify the context is maintained
    """
    print("=" * 70)
    print("PHASE 5: TESTING STATEFULNESS (SHORT-TERM MEMORY)")
    print("=" * 70)
    
    # Test configuration
    test_chat_id = -1001234567890  # Fake group chat ID
    test_user_id = 123456789       # Fake user ID
    
    print("\n📋 Test Setup:")
    print(f"   Chat ID: {test_chat_id}")
    print(f"   User ID: {test_user_id}")
    
    # ========================================================================
    # TEST 1: Create initial event (should be saved to context)
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 1: Creating Initial Event")
    print("=" * 70)
    
    initial_message = "Let's meet tomorrow at 2pm at COM1"
    print(f"\n💬 Group Message: '{initial_message}'")
    
    await handle_group_listener(initial_message, test_chat_id, test_user_id)
    
    # Check if context was saved
    if test_chat_id in chat_context:
        print(f"\n✅ SUCCESS: Event ID saved to context: {chat_context[test_chat_id]}")
    else:
        print("\n❌ FAILED: No context saved!")
        return
    
    # Wait a bit to let async operations complete
    await asyncio.sleep(2)
    
    # ========================================================================
    # TEST 2: Try to update the event
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 2: Updating Event Time")
    print("=" * 70)
    
    update_message = "Actually, let's change it to 3pm instead"
    print(f"\n💬 Group Message: '{update_message}'")
    
    await handle_group_listener(update_message, test_chat_id, test_user_id)
    
    # Wait for async operations
    await asyncio.sleep(2)
    
    # ========================================================================
    # TEST 3: Create a new event (should NOT be an update)
    # ========================================================================
    print("\n" + "=" * 70)
    print("TEST 3: Creating New Event (Not an Update)")
    print("=" * 70)
    
    new_event_message = "Dinner at 7pm tomorrow at Deck"
    print(f"\n💬 Group Message: '{new_event_message}'")
    
    await handle_group_listener(new_event_message, test_chat_id, test_user_id)
    
    # Check if context was updated
    await asyncio.sleep(2)
    
    # ========================================================================
    # TEST 4: Display final context state
    # ========================================================================
    print("\n" + "=" * 70)
    print("FINAL CONTEXT STATE")
    print("=" * 70)
    print(f"\nChat Context: {chat_context}")
    
    if test_chat_id in chat_context:
        print(f"\n✅ Group {test_chat_id} has memory of event ID: {chat_context[test_chat_id]}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\n💡 Notes:")
    print("   - Check the console logs above to see the full flow")
    print("   - Verify that TEST 2 triggered update detection")
    print("   - Verify that TEST 3 created a new event (not an update)")
    print("   - The context should contain the event ID from TEST 3")

if __name__ == "__main__":
    asyncio.run(test_statefulness())
