# app/services/crud.py
from datetime import datetime, timedelta
from app.services.db import supabase
from app.schemas.event import Event


async def check_conflicts(start_time: str, end_time: str, user_id: int = None) -> list:
    """
    Checks if a proposed time slot overlaps with existing events for a specific user.
    
    Args:
        start_time: ISO 8601 start time
        end_time: ISO 8601 end time
        user_id: User ID to check conflicts for (optional, but recommended)
    
    Returns:
        List of conflicting events
    """
    try:
        query = supabase.table("events").select("*")
        
        # Filter by user_id if provided (important to avoid cross-user conflicts)
        if user_id:
            query = query.eq("user_id", user_id)
        
        # Check for time overlap using standard interval logic:
        # Events overlap if: start1 < end2 AND end1 > start2
        response = query.filter(
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
    
async def get_event_by_id(event_id: int):
    """
    Retrieves a single event by its ID.
    Args:
        event_id: The primary key ID of the event.
    Returns:
        Event data dict or None if not found.
    """
    try:
        response = supabase.table("events").select("*").eq("id", event_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"⚠️ Get Event Error: {e}")
        return None

async def update_event(event_id: int, updates: dict):
    """
    Updates an existing event in Supabase.
    Args:
        event_id: The primary key ID of the event to modify.
        updates: Dictionary of fields to change (e.g., {'start_time': '...'})
    """
    # 1. Clean data: Remove None/null values to prevent accidental erasure
    clean_updates = {k: v for k, v in updates.items() if v is not None}
    
    if not clean_updates:
        return {"status": "ignored", "message": "No valid fields to update."}

    print(f"   📝 Updating Event {event_id} with: {clean_updates}")

    # 2. Conflict Check (Only if time is being updated)
    if "start_time" in clean_updates:
        start = clean_updates["start_time"]
        end = clean_updates.get("end_time")
        
        if end:
            # Get the user_id from the existing event for conflict checking
            existing_event = await get_event_by_id(event_id)
            user_id = existing_event.get("user_id") if existing_event else None
            
            conflicts = await check_conflicts(start, end, user_id)
            conflicts = [c for c in conflicts if c.get('id') != event_id]
            
            if conflicts:
                return {
                    "status": "conflict",
                    "message": f"Update conflicts with {len(conflicts)} event(s).",
                    "conflicting_events": conflicts
                }

    # 3. Perform the Update
    try:
        response = supabase.table("events").update(clean_updates).eq("id", event_id).execute()
        
        if response.data:
            return {"status": "success", "data": response.data[0]}
        else:
            return {"status": "error", "message": "Event not found or no rows updated."}
            
    except Exception as e:
        print(f"⚠️ Update DB Error: {e}")
        return {"status": "error", "message": str(e)}

async def save_event_to_db(event_data: Event, user_id: int = None):
    """
    Saves event to Supabase.
    UPDATED: Now accepts user_id to link events to specific users.
    """
    payload = event_data.model_dump(mode='json')
    
    if user_id:
        payload["user_id"] = user_id

    # Conflict Check - pass user_id to only check conflicts for this specific user
    conflicts = await check_conflicts(payload["start_time"], payload["end_time"], user_id)
    
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
    
async def get_users_with_events_for_date(date_str: str) -> list:
    """
    Finds all unique user_ids that have at least one event on the target date.
    Args:
        date_str: YYYY-MM-DD format (usually today + 1 day)
    """
    start_of_day = f"{date_str}T00:00:00"
    end_of_day = f"{date_str}T23:59:59"

    try:
        response = supabase.table("events").select("user_id")\
            .gte("start_time", start_of_day)\
            .lte("start_time", end_of_day)\
            .execute()
        
        if response.data:
            unique_users = list(set(u['user_id'] for u in response.data if u['user_id']))
            return unique_users
        return []
        
    except Exception as e:
        print(f"⚠️ Batch User Query Error: {e}")
        return []

# app/services/crud.py

async def save_scavenged_events_batch(events: list[Event], user_id: int):
    """
    Architected for Phase 6. Efficiently saves multiple scavenged events.
    """
    if not events:
        return {"status": "ignored", "message": "No events to save."}

    # Convert all Pydantic models to dicts and inject user_id
    payloads = []
    for e in events:
        data = e.model_dump(mode='json')
        data["user_id"] = user_id
        # Source is explicitly set to web_scavenge by the agent
        payloads.append(data)

    try:
        # Supabase .insert() accepts a list for bulk insertion
        response = supabase.table("events").insert(payloads).execute()
        return {
            "status": "success", 
            "count": len(response.data) if response.data else 0
        }
    except Exception as e:
        print(f"⚠️ Batch Save Error: {e}")
        return {"status": "error", "message": str(e)}
