"""
Telegram Utility Functions (Member B)
Handles parsing and processing of Telegram updates
"""

from typing import Optional, Dict, Any


def parse_telegram_update(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Safely extracts information from Telegram updates and returns a clean dictionary.
    
    This function is defensive - Telegram sends various update types:
    - Regular messages
    - edited_message (someone fixed a typo)
    - my_chat_member (bot added/removed from group)
    - channel_posts, etc.
    
    We only care about regular messages for now.
    
    Args:
        payload: The raw JSON from Telegram's webhook
        
    Returns:
        A dictionary containing:
        - chat_id: The ID of the room (to send replies back)
        - user_id: The ID of the person (needed for database later)
        - chat_type: Critical flag - "private", "group", or "supergroup"
        - text: The actual message content
        
        Returns None if this is not a regular message (ignore it)
    
    Example Telegram payload structure:
    {
        "update_id": 123456789,
        "message": {
            "message_id": 1234,
            "from": {
                "id": 987654321,
                "first_name": "John",
                "username": "john_doe"
            },
            "chat": {
                "id": -1001234567890,
                "type": "supergroup",
                "title": "My Group"
            },
            "text": "Meet on Friday at 4pm"
        }
    }
    """
    
    # Defensive check #1: Does this payload contain a "message"?
    if "message" not in payload:
        # This might be an edited_message, my_chat_member, etc.
        # We ignore these for now
        return None
    
    message = payload["message"]
    
    # Defensive check #2: Does the message have text content?
    # (Some messages are photos, stickers, etc. without text)
    if "text" not in message:
        return None
    
    # Defensive check #3: Ensure critical fields exist
    if "chat" not in message or "from" not in message:
        return None
    
    # Extract the clean data
    try:
        clean_data = {
            "chat_id": message["chat"]["id"],          # Where to send replies
            "user_id": message["from"]["id"],          # Who sent this message
            "chat_type": message["chat"]["type"],      # "private", "group", or "supergroup"
            "text": message["text"].strip()            # The actual message (cleaned)
        }
        
        return clean_data
    
    except KeyError as e:
        # If any field is missing, log and return None
        print(f"⚠️ Failed to parse Telegram update: Missing key {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"⚠️ Unexpected error parsing Telegram update: {e}")
        return None
