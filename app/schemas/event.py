"""
Event Schema - The Shared Contract
This Pydantic model enforces structured data output from the LLM
and ensures consistency between the brain (AI), storage (DB), and body (Telegram UI).
"""

from pydantic import BaseModel, Field
from typing import Optional


class Event(BaseModel):
    """
    Event model that forces LLM to output structured data instead of random text.
    
    This serves as the contract between:
    - LLM extraction (Member A)
    - Database storage (Member A)
    - Telegram display (Member B)
    """
    
    title: str = Field(
        ...,
        description="The headline for notifications (e.g., 'CS2103 Lecture', 'Team Meeting')"
    )
    
    start_time: str = Field(
        ...,
        description="ISO 8601 format: YYYY-MM-DDTHH:MM:SS (e.g., '2026-01-17T14:00:00'). Used for sorting."
    )
    
    end_time: Optional[str] = Field(
        None,
        description="ISO 8601 format: YYYY-MM-DDTHH:MM:SS. Optional for calendar blocking."
    )
    
    location: Optional[str] = Field(
        None,
        description="Physical or virtual location context (e.g., 'COM1-0210', 'Zoom Link')"
    )
    
    web_enrichment: Optional[str] = Field(
        None,
        description="Agent-filled field with login links, map URLs, or 'Personal event - no info available'"
    )
    
    raw_text: Optional[str] = Field(
        None,
        description="The original message from user - backup in case AI misinterprets"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "title": "CS2103 Lecture",
                "start_time": "2026-01-24T14:00:00",
                "end_time": "2026-01-24T16:00:00",
                "location": "COM1-0210",
                "web_enrichment": "https://nus-cs2103-ay2526s2.github.io/website/",
                "raw_text": "Guys let's meet for CS2103 lecture on Jan 24th at 2pm"
            }
        }
