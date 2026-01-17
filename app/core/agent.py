# app/core/agent.py
import os
from tavily import TavilyClient
from dotenv import load_dotenv
from app.schemas.event import Event

load_dotenv()

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