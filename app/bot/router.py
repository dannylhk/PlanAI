"""
Bot Router - The Brain (Member B)
Routes messages to the correct handler based on chat type
"""
from typing import Dict, Any
from app.core.llm import extract_event_from_text, check_event_intent
from app.bot.responses import format_event_confirmation, send_message



async def process_message(clean_data: Dict[str, Any]) -> None:
    """
    The brain of the bot - routes messages to the correct function.
    
    This is the critical routing logic that determines:
    - Private chat → Master Hub (Active command center)
    - Group chat → Listener (Passive event detection)
    
    Args:
        clean_data: The clean dictionary from parse_telegram_update containing:
            - chat_id: Where to send replies
            - user_id: Who sent the message
            - chat_type: "private", "group", or "supergroup"
            - text: The message content
    """
    
    chat_type = clean_data.get("chat_type")
    chat_id = clean_data.get("chat_id")
    user_id = clean_data.get("user_id")
    text = clean_data.get("text")
    
    print(f"\n🧠 ROUTER: Processing message from {chat_type} chat")
    print(f"   Chat ID: {chat_id}")
    print(f"   Text: {text}")
    
    # Route to the correct handler based on chat type
    if chat_type == "private":
        # This is a direct message to the bot - the "Master Hub"
        print("   → Routing to: Master Hub (handle_hub_command)")
        await handle_hub_command(text, user_id)
    
    elif "group" in chat_type:
        # This is a group or supergroup message - the "Listener"
        print("   → Routing to: Group Listener (handle_group_listener)")
        await handle_group_listener(text, chat_id)
    
    else:
        # Unknown chat type - this shouldn't happen, but be defensive
        print(f"   ⚠️ WARNING: Unknown chat_type '{chat_type}' - ignoring message")


async def handle_hub_command(text: str, user_id: int):
    """
    Handler for Master Hub (Private Chat).
    
    BEST PRACTICE (Software Engineering):
    - Start with simple print statements to verify the pipeline works
    - Add complexity incrementally (don't try to build everything at once)
    """
    print(f"\n💬 HUB: User {user_id} sent private command: {text}")
    # TODO: Later, we will add Member A's DB logic here


async def handle_group_listener(text: str, chat_id: int):
    """
    STEP 3: Mock Intelligence Filter
    
    Instead of expensive LLM calls during development, we use simple keyword matching.
    This allows rapid testing without burning API credits.

    """

    print(f"\n👂 LISTENER: Heard '{text}' in Group {chat_id}")
    
    # Mock Event Detection (Simple keyword matching)
    # Later: This will be replaced with Member A's is_event_intent() LLM call
    is_meeting = await check_event_intent(text)  # FIX: Added 'await'
    
    if is_meeting:
        print("   ✅ Event Detected! Asking for confirmation...")
        
        # Call Member A's extract_datetime_from_text()
        confirmed_event = await extract_event_from_text(text)
        
        # DEFENSIVE PROGRAMMING: Check if extraction was successful
        if confirmed_event is None:
            print("   ❌ ERROR: Failed to extract event details (Member A's function returned None)")
            print("   → This might be due to:")
            print("      - Gemini API error (check Member A's code)")
            print("      - Invalid text format")
            print("      - Missing API key")
            # Don't crash - just return gracefully
            return
        
        # Format the text nicely
        confirmed_msg = format_event_confirmation(confirmed_event)
        
        # Send it to Telegram
        result = await send_message(chat_id, confirmed_msg)
        
        if result.get("ok"):
            print(f"   ✅ Confirmation message sent successfully!")
        else:
            print(f"   ❌ Failed to send message: {result.get('error')}")

    else:
        print("   ⏭️  Ignoring noise (not an event)...")
