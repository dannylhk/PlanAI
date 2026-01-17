from fastapi import FastAPI
from app.api import webhook
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Connect the router (the website that receives the message from telegram) to main
app.include_router(webhook.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "PlanAI is running"}