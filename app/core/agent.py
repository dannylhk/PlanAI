# app/core/agent.py
"""
Agent Module - Member A's Research Functions
Contains web search and enrichment functionality for PlanAI
"""
import os
from typing import List
from pydantic import BaseModel
from app.schemas.event import Event
from app.core.llm import client, MODEL_ID
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Tavily client for web search
try:
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
except:
    tavily = None


# ============================================================================
# PHASE 3: EVENT ENRICHMENT (Single Event Web Search)
# ============================================================================

async def enrich_event(event: Event) -> Event:
    """
    Searches the web for context (Venue location, Course URL, etc.)
    and appends it to the event object.
    
    Args:
        event: Event Pydantic model instance
        
    Returns:
        Enriched Event with web_enrichment populated
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


# ============================================================================
# PHASE 6: ACTIVE RESEARCH MODE (Scavenging)
# ============================================================================

class ScavengeResponse(BaseModel):
    """Wrapper for LLM response containing list of events"""
    events: List[Event]


async def scavenge_events(topic: str) -> List[Event]:
    """
    Member A: The Research Agent.
    
    Performs active web search for a given topic and extracts all relevant
    events, deadlines, and dates using LLM parsing.
    
    Args:
        topic: The search topic (e.g., "CS2103 deadlines", "NUS Academic Calendar")
        
    Returns:
        List[Event]: List of Event Pydantic models with source="web_scavenge"
        
    Schema Handshake:
        - All returned events have source: "web_scavenge"
        - Member B can differentiate from chat-extracted events (source: "telegram")
    """
    if not tavily:
        print("⚠️ Tavily Key missing. Cannot scavenge events.")
        return []

    # Build search query optimized for finding dates/deadlines
    query = f"{topic} schedule deadlines dates 2026 Singapore"
    print(f"🕵️ Scavenging: '{query}'...")

    try:
        # Perform advanced web search
        search_results = tavily.search(
            query=query, 
            search_depth="advanced", 
            max_results=3
        )
        
        # Combine all search result content for LLM processing
        context_text = "\n".join([r['content'] for r in search_results['results']])
        
        if not context_text.strip():
            print("   📭 No search results content")
            return []

        # LLM prompt for structured event extraction
        system_prompt = f"""Extract ALL specific events, deadlines, and dates related to '{topic}' from the provided text.

RULES:
1. Return a JSON object with a key "events" containing a list of Event objects.
2. Each event must have: title, start_time (ISO 8601: YYYY-MM-DDTHH:MM:SS)
3. If no specific time is mentioned, use T09:00:00 as default
4. If the year is missing, assume 2026
5. Set 'source' to 'web_scavenge' for all events
6. Extract as many relevant events as possible from the text
7. Include end_time if duration is mentioned (otherwise set to 1 hour after start)"""

        # Use OpenAI structured output for the batch of events
        completion = await client.beta.chat.completions.parse(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract events from this text:\n\n{context_text}"}
            ],
            response_format=ScavengeResponse,
        )
        
        # Access the parsed events from the wrapper
        events = completion.choices[0].message.parsed.events
        
        print(f"   ✅ Extracted {len(events)} events from web search")
        
        # Ensure all events have source set to web_scavenge
        for event in events:
            event.source = "web_scavenge"
        
        return events

    except Exception as e:
        print(f"⚠️ Scavenge Error: {e}")
        return []
