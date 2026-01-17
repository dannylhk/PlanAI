from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Event(BaseModel):
    """
    Standard Event model for PlanAI.
    """
    title: str = Field(..., description="The headline for notifications (e.g., 'CS2103 Lecture', 'Team Meeting')")
    start_time: str = Field(..., description="ISO 8601 start time (e.g., '2026-01-17T14:00:00')")
    
    end_time: str = Field(..., description="ISO 8601 end time") # Kept required as per your logic, or make Optional if you prefer
    
    location: Optional[str] = Field(None, description="Physical or virtual location context")
    description: Optional[str] = Field(None, description="Details or agenda")
    
    source: Optional[str] = Field("telegram", description="Origin: 'telegram', 'email', 'manual'")
    
    context_notes: Optional[str] = Field(None, description="The original raw message text for reference")

    web_enrichment: Optional[Dict[str, Any]] = Field(
        None, 
        description="Agent-filled data (links, map_url, summary) from Phase 3"
    )

    class Config:
        """Pydantic configuration with examples for documentation"""
        json_schema_extra = {
            "example": {
                "title": "CS2103 Lecture",
                "start_time": "2026-01-24T14:00:00",
                "end_time": "2026-01-24T16:00:00",
                "location": "COM1-0210",
                "source": "telegram",
                "context_notes": "Guys let's meet for CS2103 lecture on Jan 24th at 2pm",
                "web_enrichment": {
                    "url": "https://nus-cs2103.github.io",
                    "map_link": "https://maps.google.com/..."
                }
            }
        }