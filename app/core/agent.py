# app/core/agent.py
import os
from tavily import TavilyClient
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from app.schemas.event import Event

from typing import List

load_dotenv()
from app.core.llm import client, MODEL_ID

try:
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
except:
    tavily = None

async def enrich_event(event: Event) -> Event:
    """
    Searches the web for context (Venue location, Course URL, etc.)
    and appends it to the event object.
    """
    if not tavily:
        print("⚠️ Tavily Key missing. Skipping enrichment.")
        return event

    # Search Logic
    query = f"{event.title} {event.location or ''} official site or map Singapore"
    print(f"🕵️ Searching: '{query}'...")

    try:
        response = tavily.search(query=query, search_depth="basic", max_results=1)
        
        if response['results']:
            top_result = response['results'][0]
            event.web_enrichment = f"🔗 Found: {top_result['title']} ({top_result['url']})"
            
            if not event.location:
                event.location = top_result['url']
                
    except Exception as e:
        print(f"⚠️ Search Error: {e}")
    
    return event
class ScavengeResponse(BaseModel):
    events: List[Event]

async def scavenge_events(topic: str) -> List[Event]:
    if not tavily:
        return []

    query = f"{topic} dates deadlines schedule 2026 Singapore"
    
    try:
        search_results = tavily.search(query=query, search_depth="advanced", max_results=3)
        context_text = "\n".join([r['content'] for r in search_results['results']])

        prompt = f"""
        Extract ALL specific events, deadlines, and dates related to '{topic}' from the text.
        
        TEXT:
        {context_text}
        
        RULES:
        1. Return a JSON object with a key "events" containing a list of Event objects.
        2. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS).
        3. If no time is mentioned, use T09:00:00.
        4. If the year is missing, use 2026.
        5. Set 'source' to 'web_scavenge'.
        """

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                # Pass the wrapper class instead of a raw List
                "response_schema": ScavengeResponse, 
            },
        )
        
        # Access the 'events' attribute of the wrapper
        return response.parsed.events 
        
    except Exception as e:
        print(f"⚠️ Scavenge Error: {e}")
        return []