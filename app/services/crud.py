# app/services/crud.py
from app.schemas.event import Event

# Simple in-memory list for Phase 1 Demo
MOCK_DB = []

async def save_event(event: Event) -> bool:
    """
    Saves event to the database (Mocked).
    """
    print(f"💾 [DB] Saving: {event.to_log_string()}")
    MOCK_DB.append(event)
    return True

async def get_all_events():
    return MOCK_DB