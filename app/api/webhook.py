from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook")
async def receive_telegram_update(request: Request):
    # 1. Get the raw JSON from Telegram
    payload = await request.json()
    
    # 2. Print it to your terminal (Debug mode)
    print("\n📩 NEW MESSAGE RECEIVED:")
    print(payload)
    
    # 3. Always return 200 OK, or Telegram will keep retrying forever
    return {"status": "ok"}