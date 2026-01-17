# test_phase2.py
import asyncio
from app.core.llm import check_event_intent
from app.services.crud import save_event_to_db
from app.schemas.event import Event

async def run_tests():
    print("🧪 STARTING PHASE 2 TESTS...\n")

    # --- TEST 1: The Intent Filter (LLM) ---
    print("1️⃣  Testing Intent Filter (Gemini)...")
    
    # Case A: Chatter
    chatter = "lol that's funny"
    is_plan_a = await check_event_intent(chatter)
    print(f"   Input: '{chatter}' -> Is Event? {is_plan_a} (Expected: False)")

    # Case B: Real Plan
    plan = "Let's have a team meeting tomorrow at 2pm"
    is_plan_b = await check_event_intent(plan)
    print(f"   Input: '{plan}' -> Is Event? {is_plan_b} (Expected: True)")
    
    if not is_plan_a and is_plan_b:
        print("   ✅ Intent Filter Passed!")
    else:
        print("   ❌ Intent Filter Failed.")
    
    print("-" * 30)

    # --- TEST 2: Database Save & Conflict Check ---
    print("2️⃣  Testing Database (Supabase)...")

    # Define a dummy event (Minimal fields only!)
    dummy_event = Event(
        title="Phase 2 Test Event",
        start_time="2026-12-01T10:00:00",
        end_time="2026-12-01T11:00:00",
        location="Virtual",
        description="Testing the save function",
        source="Manual Test Script"  # Optional, but good for tracking
        # web_enrichment is purposefully OMITTED to save API calls
    )

    # Case A: Save New Event
    print(f"   Attempting to save: {dummy_event.title}...")
    result = await save_event_to_db(dummy_event)
    
    if result["status"] == "success":
        print(f"   ✅ Save Successful! ID: {result['data'].get('id')}")
    elif result["status"] == "conflict":
        print("   ⚠️ Event already exists (Conflict detected). This is okay if you ran the test twice.")
    else:
        print(f"   ❌ Save Failed: {result}")

    # Case B: Force a Conflict (Try saving the EXACT same time again)
    print("   Attempting to save duplicate (expecting conflict)...")
    conflict_result = await save_event_to_db(dummy_event)
    
    if conflict_result["status"] == "conflict":
        print("   ✅ Conflict Logic Works! It blocked the double-booking.")
    else:
        print(f"   ❌ Conflict Logic Failed. Result: {conflict_result['status']}")

if __name__ == "__main__":
    asyncio.run(run_tests())