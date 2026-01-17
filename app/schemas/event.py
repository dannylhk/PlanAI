# app/schemas/event.py
from pydantic import BaseModel, Field
from typing import Optional

class Event(BaseModel):
    title: str = Field(..., description="Short title of the event")
    start_time: str = Field(..., description="ISO 8601 format: YYYY-MM-DDTHH:MM:SS")
    end_time: Optional[str] = Field(description="ISO 8601 format")
    location: Optional[str] = Field(description="Physical location or URL")
    
    source: str = Field(description="Source channel (always set to 'telegram')")
    context_notes: str = Field(..., description="Original text or summary")
    web_enrichment: Optional[str] = Field(description="Links found by the AI agent")

    def to_log_string(self):
        return f"📅 {self.title} @ {self.start_time} | 📍 {self.location or 'No Loc'}"