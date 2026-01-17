from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Event(BaseModel):
    """
    Standard Event model for PlanAI.
    """
    title: str = Field(..., description="The name of the event")
    start_time: str = Field(..., description="ISO 8601 start time")
    end_time: str = Field(..., description="ISO 8601 end time")
    
    location: Optional[str] = None
    description: Optional[str] = None
    
    source: Optional[str] = Field(None, description="Where this event came from (e.g., 'user_message', 'email')")
    context_notes: Optional[str] = Field(None, description="Raw context or original text for reference")
    
    web_enrichment: Optional[Dict[str, Any]] = Field(None, description="Data from Tavily/Maps (links, reviews, images)")