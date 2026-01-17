"""
STEP 4: Connect the Wires
The webhook is the "mailbox" - it receives data from Telegram.
Now we connect it to the Parser (utils.py) and Router (router.py).

BEST PRACTICE (System Architecture):
- Separation of Concerns: Webhook → Parser → Router → Handler
- Each layer has ONE job (Single Responsibility Principle)
- This makes debugging easier: you know exactly where to look
"""

from fastapi import APIRouter, Request
from app.bot.utils import parse_telegram_update
from app.bot.router import process_message

router = APIRouter()


@router.post("/webhook")
async def receive_telegram_update(request: Request):
    """
    The entry point for all Telegram updates.
    
    Flow:
    1. Receive raw JSON from Telegram
    2. Parse it (extract clean data)
    3. Route it (send to correct handler)
    4. Return 200 OK (or Telegram will retry forever)
    
    BEST PRACTICE (API Design):
    - Always return 200 OK quickly
    - Process logic asynchronously
    - Log errors but don't crash (defensive programming)
    """
    
    # 1. Get the raw JSON from Telegram
    payload = await request.json()
    
    # 2. Print it to your terminal (Debug mode - REMOVE in production)
    print("\n📩 NEW MESSAGE RECEIVED:")
    print(payload)
    
    # 3. Parse the payload (defensive - returns None if not a message)
    clean_data = parse_telegram_update(payload)
    
    if clean_data is None:
        # Not a regular message (edited_message, my_chat_member, etc.)
        print("   ⏭️  Skipping non-message update")
        return {"status": "ok"}
    
    # 4. Route to the correct handler (MUST use await - it's async)
    await process_message(clean_data)
    
    # 5. Always return 200 OK, or Telegram will keep retrying forever
    # BEST PRACTICE: Return fast, process in background
    return {"status": "ok"}
