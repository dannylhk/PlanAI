"""
PlanAI - Main Application Entry Point
FastAPI server with APScheduler for nightly briefings
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import os

load_dotenv()

# Import the nightly briefing function
from app.bot.briefing import send_nightly_briefing

# ============================================================================
# PHASE 7: APScheduler Setup (Best Practice with Lifespan)
# ============================================================================

# Global scheduler instance
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI (recommended over @app.on_event).
    
    This handles startup and shutdown events cleanly:
    - On startup: Start the APScheduler with 9 PM nightly briefing
    - On shutdown: Gracefully stop the scheduler
    
    Best Practice:
    - Use asynccontextmanager instead of deprecated @app.on_event
    - Use timezone-aware scheduling for Singapore (UTC+8)
    """
    # ========== STARTUP ==========
    print("🚀 Starting PlanAI...")
    
    # Add the nightly briefing job at 9 PM Singapore time
    # CronTrigger(hour=21, minute=0) = 9:00 PM daily
    scheduler.add_job(
        send_nightly_briefing,
        CronTrigger(hour=21, minute=0, timezone="Asia/Singapore"),
        id="nightly_briefing",
        name="9 PM Nightly Briefing",
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    print("⏰ Scheduler started - Nightly briefing scheduled for 9:00 PM SGT")
    
    yield  # App is running here
    
    # ========== SHUTDOWN ==========
    print("🛑 Shutting down PlanAI...")
    scheduler.shutdown(wait=False)
    print("⏰ Scheduler stopped")


# Create FastAPI app with lifespan
app = FastAPI(
    title="PlanAI",
    description="Your AI-powered group calendar assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Connect the webhook router
from app.api import webhook
app.include_router(webhook.router, prefix="/api")


@app.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "PlanAI is running", "scheduler": "active"}


@app.get("/scheduler/status")
def scheduler_status():
    """
    Check scheduler status and next run time.
    Useful for debugging the nightly briefing schedule.
    """
    jobs = scheduler.get_jobs()
    job_info = []
    
    for job in jobs:
        job_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else "Not scheduled"
        })
    
    return {
        "scheduler_running": scheduler.running,
        "jobs": job_info
    }
