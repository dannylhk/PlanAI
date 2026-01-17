"""
Bot Router - The Brain (Member B)
Routes messages to the correct handler based on chat type
"""

from typing import Dict, Any


async def handle_hub_command(text: str, user_id: int):
    print(f"� HUB: User {user_id} sent private command: {text}")
    # TODO: Later, we will add Member A's DB logic here

async def handle_group_listener(text: str, chat_id: int):
    print(f"� LISTENER: Heard '{text}' in Group {chat_id}")
    # TODO: Later, we will add the "Is this a meeting?" filter here
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
