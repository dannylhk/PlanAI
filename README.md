<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/Framework-FastAPI-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/AI-OpenAI%20GPT--4o-412991" alt="OpenAI">
  <img src="https://img.shields.io/badge/Platform-Telegram-0088cc" alt="Telegram">
</p>

<h1 align="center">🗓️ PlanAI</h1>

<p align="center">
  <strong>Your AI-Powered Group Calendar Assistant</strong><br>
  The intelligent command center that unifies your chaotic communication channels into one seamless schedule.
</p>

---

## 🎯 The Problem We Solve

**Students today are drowning in information scattered across multiple platforms:**

| Channel                | Problem                                      |
| ---------------------- | -------------------------------------------- |
| 📧 **Official Emails (coming soon)** | Important deadlines buried in long chains    |
| 💬 **Telegram Groups** | Event details lost in 500+ unread messages   |
| 📅 **Calendar Apps (coming soon)**   | Empty because manual entry is tedious        |
| 🧠 **Human Memory**    | Unreliable for tracking multiple commitments |

### The Market Gap

Traditional calendar apps are **passive storage bins**—they only work if you manually enter every event. But students receive scheduling information through **conversations**, not forms.

**PlanAI bridges this gap** by acting as an **active AI agent** that:

- 👂 **Listens** to your group chats for event mentions
- 🧠 **Understands** natural language ("let's meet tomorrow at 2pm")
- 🔍 **Researches** the web for deadlines you might miss
- ⚠️ **Warns** you about schedule conflicts in real-time
- 📲 **Proactively** reminds you of tomorrow's events every night

---

## ✨ Key Features

### 1. 👂 Passive Group Chat Listener

> _Never miss an event mentioned in your group chats again_

Add PlanAI to any Telegram group, and it will automatically:

- Detect event-related messages using AI
- Extract event details (time, location, title)
- Check for schedule conflicts
- Send you a **private notification** (no group spam!)

```
👥 Group Chat:
"Let's meet tomorrow at 2pm at COM1"

🤖 PlanAI (privately to you):
✅ Event Added!
📌 Meeting
🕐 Jan 18, 2:00 PM
📍 COM1
```

### 2. 📅 `/agenda` - Daily Dashboard

> _See your entire day at a glance_

**Command:** `/agenda` or `"what is my plan today?"`

```
📅 Your Agenda for Saturday, January 18, 2026

09:00 - CS2103T Lecture
📍 I3 Auditorium

14:00 - Team Meeting
📍 COM1-0210

16:00 - Gym Session

18:00 - Dinner with Friends
📍 UTown
⚠️ CONFLICT
```

**Design Principles:**

- ✅ Celebratory empty state ("No events! Enjoy your free time!")
- ✅ Visual timeline with bold times
- ✅ Location shown only when available
- ✅ Clear conflict warnings

### 3. 🕵️ `/track` - Active Research Mode

> _Let AI find deadlines for you_

Don't know the important dates? PlanAI searches the web and extracts deadlines automatically.

**Command:** `/track [topic]`

```
/track CS2103 deadlines
```

```
🔍 Research Complete: CS2103 deadlines

📋 Found 5 events:

1. CS2103 PE-D
   📅 Mar 21, 2026, 4:00 PM

2. CS2103 Final Exam
   📅 Apr 26, 2026, 9:00 AM

3. Team Project Submission
   📅 Apr 15, 2026, 11:59 PM

...

✅ Added to your calendar!
🌐 Source: Web Research
```

### 4. 🧠 Statefulness - Smart Update Detection

> _Context-aware conversations_

PlanAI remembers the last event discussed in each group and intelligently handles updates:

```
👤 "Meeting tomorrow at 2pm at COM1"
🤖 ✅ Event saved!

👤 "Actually, change it to 3pm"
🤖 ✅ Event Updated!
   ⏰ Time: Jan 18, 2PM → Jan 18, 3PM
```

**Not confused by new events:**

```
👤 "Dinner at 7pm tomorrow"
🤖 ✅ New event saved! (not an update)
```

### 5. 🌙 Nightly Briefing

> _Proactive reminders at 9 PM_

Every night at 9 PM (Singapore time), PlanAI sends you tomorrow's schedule:

```
🌙 Tomorrow's Schedule
📅 Sunday, January 19, 2026

You have 3 events tomorrow:

09:00 - CS2103T Lecture
   📍 I3 Auditorium

14:00 - Team Meeting
   📍 COM1-0210

18:00 - Dinner with Friends
   📍 UTown

💪 Busy day ahead! You've got this!
```

**Demo Command:** `/force_briefing` - Test the nightly briefing instantly

### 6. ⚠️ Real-Time Conflict Detection

> _Never double-book yourself again_

When adding any event, PlanAI automatically checks for overlapping schedules:

```
⚠️ CONFLICT DETECTED

Your new event overlaps with:
1. CS2103T Lecture (Jan 18, 2:00 PM)

💡 Please choose a different time.
```

### 7. 🔗 Web Enrichment

> _Automatic context for your events_

When you add an event, PlanAI searches the web for relevant information:

```
✅ Event Added!
📌 CS2103T Lecture
🕐 Jan 24, 2:00 PM
📍 I3 Auditorium

🔗 More Information
→ https://nus-cs2103.github.io/website/
```

### 8. 🗑️ `/clearall` - Clear Your Day & Rest!

> _When you need a break from productivity_

Sometimes you just need to clear your schedule and take a day off. PlanAI understands!

**Command:** `/clearall`

```
🗑️ Cleared 4 events...

💥 KABOOM! Your to-do list has exploded into confetti!

🎊 Congratulations! You've unlocked: FREE TIME! 🎊

Quick, do nothing before responsibilities find you! 🏃‍♂️

Remember: You can't be late if you have nowhere to be *taps head*
```

**Features:**

- ✅ Clears all events for today
- ✅ Random goofy messages encouraging you to rest
- ✅ Smart empty state detection ("Your schedule was already empty. You absolute legend. 👑")

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         TELEGRAM                                │
│                    (Groups + Private DMs)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Webhook                            │
│                    (app/api/webhook.py)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Message Router                             │
│                   (app/bot/router.py)                           │
│                                                                 │
│   ┌─────────────────┐              ┌─────────────────────────┐  │
│   │  Private Chat   │              │     Group Chat          │  │
│   │  (Master Hub)   │              │     (Listener)          │  │
│   │                 │              │                         │  │
│   │ • /agenda       │              │ • Event Detection       │  │
│   │ • /track        │              │ • Update Detection      │  │
│   │ • /clearall     │              │ • Conflict Checking     │  │
│   │ • /force_brief  │              │                         │  │
│   └────────┬────────┘              └───────────┬─────────────┘  │
└────────────┼───────────────────────────────────┼────────────────┘
             │                                   │
             ▼                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI Layer (OpenAI GPT-4o)                   │
│                      (app/core/llm.py)                          │
│                                                                 │
│   • extract_event_from_text() - Natural language → Event       │
│   • detect_update_intent() - Is this an update?                 │
│   • check_event_intent() - Fast keyword filter                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Research Agent (Tavily)                    │
│                    (app/core/agent.py)                          │
│                                                                 │
│   • scavenge_events() - Web search → Events                     │
│   • enrich_event() - Add web context                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supabase (PostgreSQL)                      │
│                   (app/services/crud.py)                        │
│                                                                 │
│   • save_event_to_db() - With conflict detection                │
│   • get_events_by_date() - For /agenda & briefings              │
│   • update_event() - For statefulness updates                   │
│   • delete_events_by_date() - For /clearall command             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key
- Supabase Project (free tier works!)
- Tavily API Key (for web search)

### Installation

```bash
# Clone the repository
git clone https://github.com/dannylhk/PlanAI.git
cd PlanAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
TAVILY_API_KEY=your_tavily_api_key
```

### Database Setup

Create an `events` table in Supabase:

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    location TEXT,
    description TEXT,
    source TEXT DEFAULT 'telegram',
    context_notes TEXT,
    web_enrichment TEXT,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Setting Up Telegram Webhook

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<YOUR_DOMAIN>/api/telegram"
```

---

## 🧪 Test Cases - Try These in Your Telegram!

### Test 1: Basic Event Creation

**In a group chat with the bot:**

```
Let's meet tomorrow at 2pm at COM1
```

**Expected:** Private notification with event details

### Test 2: Event Update (Statefulness)

**After Test 1, in the same group:**

```
Actually, change it to 3pm
```

**Expected:** Update confirmation showing time change

### Test 3: New Event Detection

**After Test 2, in the same group:**

```
Dinner at 7pm at UTown
```

**Expected:** New event created (not treated as update)

### Test 4: Conflict Detection

**In a group chat:**

```
Meeting at 3pm tomorrow at NUS
```

_If you already have an event at 3pm:_
**Expected:** Conflict warning with existing event details

### Test 5: Daily Agenda

**In private chat with bot:**

```
/agenda
```

**Expected:** Beautiful timeline of today's events

### Test 6: Natural Language Agenda

**In private chat with bot:**

```
what is my plan today?
```

**Expected:** Same agenda output as `/agenda`

### Test 7: Active Research

**In private chat with bot:**

```
/track NUS academic calendar 2026
```

**Expected:** List of academic deadlines added to your calendar

### Test 8: Force Nightly Briefing

**In private chat with bot:**

```
/force_briefing
```

**Expected:** Tomorrow's schedule preview

### Test 9: Empty State

**In private chat (with no events today):**

```
/agenda
```

**Expected:** 🎉 No events scheduled for today. Enjoy your free time!

### Test 10: Location Enrichment

**In a group chat:**

```
CS2103T lecture tomorrow at 2pm at I3
```

**Expected:** Event card with web enrichment link to course website

### Test 11: Clear All Events

**In private chat with bot:**

```
/clearall
```

**Expected:** All today's events cleared + goofy rest message encouraging you to relax

### Test 12: Clear All (Empty State)

**In private chat (with no events today):**

```
/clearall
```

**Expected:** Message saying "Your schedule was already empty. You absolute legend. 👑"

---

## 📁 Project Structure

```
PlanAI/
├── main.py                 # FastAPI entry + APScheduler (9 PM briefing)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
│
├── app/
│   ├── api/
│   │   └── webhook.py      # Telegram webhook endpoint
│   │
│   ├── bot/
│   │   ├── router.py       # Message routing brain
│   │   ├── responses.py    # Telegram message formatting
│   │   ├── briefing.py     # Nightly briefing logic
│   │   ├── date_utils.py   # Date formatting utilities
│   │   └── utils.py        # Helper functions
│   │
│   ├── core/
│   │   ├── llm.py          # OpenAI GPT-4o integration
│   │   ├── agent.py        # Web search agent (Tavily)
│   │   └── prompts.py      # LLM system prompts
│   │
│   ├── schemas/
│   │   └── event.py        # Pydantic Event model
│   │
│   └── services/
│       ├── crud.py         # Database operations
│       └── db.py           # Supabase client
│
└── tests/
    ├── test_agenda.py      # /agenda feature tests
    ├── test_briefing.py    # Nightly briefing tests
    ├── test_track.py       # /track command tests
    ├── test_statefulness.py # Update detection tests
    └── test_conflict_fix.py # Conflict detection tests
```

---

## 🛠️ Technologies

| Technology           | Purpose                              |
| -------------------- | ------------------------------------ |
| **FastAPI**          | High-performance async web framework |
| **Telegram Bot API** | User interface via httpx             |
| **OpenAI GPT-4o**    | Natural language understanding       |
| **Tavily**           | Web search for deadline research     |
| **Supabase**         | PostgreSQL database with real-time   |
| **APScheduler**      | Cron jobs for nightly briefings      |
| **Pydantic**         | Data validation & schemas            |
| **pytz**             | Singapore timezone handling          |

---

## 🎯 What Makes PlanAI Different?

| Feature            | Traditional Calendars      | PlanAI                          |
| ------------------ | -------------------------- | ------------------------------- |
| Event Entry        | Manual typing              | Automatic from chat             |
| Conflict Check     | After booking              | Real-time prevention            |
| Deadline Discovery | You search                 | AI searches for you             |
| Daily Reminder     | Generic notification       | Personalized briefing           |
| Group Events       | Everyone enters separately | One person mentions, all synced |
| Context Awareness  | None                       | Remembers last event            |
| Web Integration    | None                       | Auto-enriches with links        |

---

## 🔮 Future Roadmap

- [ ] 📧 Email parsing for official university announcements
- [ ] 🔄 Two-way sync with Google Calendar
- [ ] 👥 Shared group calendars
- [ ] 🔔 Custom reminder times
- [ ] 📊 Analytics dashboard
- [ ] 🌍 Multi-timezone support

---

## 👥 Contributors

| Role         | Responsibility                                      |
| ------------ | --------------------------------------------------- |
| **Member A** | LLM Integration, Web Research Agent, Database Layer |
| **Member B** | Bot UX, Message Routing, Telegram Integration       |

---

## 📄 License

MIT License - feel free to use and modify!

---

<p align="center">
  <strong>Built with ❤️ at Hack&Roll 2026</strong><br>
  <i>Because your schedule shouldn't be another thing to worry about.</i>
</p>
