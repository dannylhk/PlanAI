# app/services/crud.py
from datetime import datetime, timedelta
from app.services.db import supabase
from app.schemas.event import Event

async def check_conflicts(start_time: str, end_time: str) -> list:
    """
    Checks if a proposed time slot overlaps with existing events.
    """
    try:
        response = supabase.table("events").select("*").filter(
            "start_time", "lt", end_time
        ).filter(
            "end_time", "gt", start_time
        ).execute()
        return response.data
    except Exception as e:
        print(f"⚠️ Conflict Check Error: {e}")
        return []

async def get_events_by_date(user_id: int, date_str: str) -> list:
    """
    Retrieves all events for a specific user on a specific date.
    Args:
        user_id: Telegram User ID
        date_str: YYYY-MM-DD format
    """
    try:
        # Create Start (00:00) and End (23:59) timestamps for the query
        # Assuming date_str is "2026-01-18"
        start_of_day = f"{date_str}T00:00:00"
        end_of_day = f"{date_str}T23:59:59"
        
        print(f"   📅 Fetching agenda for {user_id} on {date_str}...")
        
        response = supabase.table("events").select("*")\
            .eq("user_id", user_id)\
            .gte("start_time", start_of_day)\
            .lte("start_time", end_of_day)\
            .order("start_time", desc=False)\
            .execute()
            
        return response.data
    except Exception as e:
        print(f"⚠️ Agenda Query Error: {e}")
        return []

async def save_event_to_db(event_data: Event, user_id: int = None):
    """
    Saves event to Supabase.
    UPDATED: Now accepts user_id to link events to specific users.
    """
    payload = event_data.model_dump(mode='json')
    
    # Inject user_id if provided
    if user_id:
        payload["user_id"] = user_id

    # Conflict Check
    conflicts = await check_conflicts(payload["start_time"], payload["end_time"])
    
    if conflicts:
        return {
            "status": "conflict",
            "message": f"Conflict detected with {len(conflicts)} event(s).",
            "conflicting_events": conflicts
        }

    try:
        response = supabase.table("events").insert(payload).execute()
        return {"status": "success", "data": response.data[0] if response.data else {}}
    except Exception as e:
        print(f" Save Error: {e}")
        return {"status": "error", "message": str(e)}