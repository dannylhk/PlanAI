# test_core.py
import asyncio
from app.core.llm import extract_event_from_text
from app.core.agent import enrich_event
from app.services.crud import save_event

async def main():
    text = "Let's meet for the Hackathon Demo next Friday at 2pm at NUS."
    
    print(f"🤖 Brain: Processing '{text}'...")
    
    event = await extract_event_from_text(text)
    
    if event:
        print(f"✅ Extracted: {event.title} @ {event.start_time}")
        
        # 2. ENRICH (Tavily)
        # This is the 'Wow' factor
        event = await enrich_event(event)
        
        # 3. SAVE (Mock DB)
        await save_event(event)
        
        print("\n🎉 FINAL JSON OBJECT:")
        print(event.model_dump_json(indent=2))
    else:
        print("❌ Extraction Failed")

if __name__ == "__main__":
    asyncio.run(main())