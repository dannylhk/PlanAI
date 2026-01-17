# app/services/crud.py
from app.services.db import supabase
from app.schemas.event import Event

async def check_conflicts(start_time: str, end_time: str) -> list:
    """
    Checks if a proposed time slot overlaps with existing events.
    Returns a list of conflicting events.
    """
    try:
        # Logic: (StartA < EndB) AND (EndA > StartB)
        response = supabase.table("events").select("*").filter(
            "start_time", "lt", end_time
        ).filter(
            "end_time", "gt", start_time
        ).execute()
        
        return response.data
    except Exception as e:
        print(f"⚠️ Conflict Check Error: {e}")
        return []

async def save_event_to_db(event_data: Event):
    """
    Saves the event to Supabase if no conflicts exist.
    Input: The Pydantic Event model from llm.py
    """
    # 1. Convert Pydantic to Dict (ISO format handles datetime serialization)
    payload = event_data.model_dump(mode='json')

    # 2. Run Conflict Check
    conflicts = await check_conflicts(payload["start_time"], payload["end_time"])
    
    if conflicts:
        return {
            "status": "conflict",
            "message": f"Conflict detected with {len(conflicts)} event(s).",
            "conflicting_events": conflicts
        }

    # 3. No conflict? Insert.
    try:
        response = supabase.table("events").insert(payload).execute()
        # Supabase V2 client often returns .data as the list of inserted rows
        return {"status": "success", "data": response.data[0] if response.data else {}}
    except Exception as e:
        print(f" Save Error: {e}")
        return {"status": "error", "message": str(e)}
    
def get_events_by_date():
    pass