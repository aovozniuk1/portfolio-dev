# Task Manager Telegram Bot

A production-ready Telegram bot for personal task management built with `python-telegram-bot` and `aiosqlite`.

## Features

- **Task Management** — Create, list, update, and delete tasks through conversational flows
- **Priority System** — Assign Low / Medium / High priority to each task
- **Status Tracking** — Move tasks through Pending → In Progress → Completed
- **Inline Keyboards** — Fully interactive UI with callback-driven navigation
- **Statistics** — View completion rates and task counts by status
- **Persistent Storage** — SQLite database via aiosqlite for async access
- **Service Layer** — Clean separation of concerns (handlers → services → database)

## Architecture

```
telegram-bot-demo/
├── main.py              # Entry point, handler registration
├── config.py            # Environment-based configuration
├── bot/
│   ├── handlers/
│   │   ├── common.py    # /start, /help, main menu
│   │   ├── tasks.py     # Task CRUD + ConversationHandler
│   │   └── errors.py    # Global error handler
│   ├── keyboards/
│   │   └── inline.py    # Inline keyboard builders
│   ├── models/
│   │   ├── user.py      # User dataclass
│   │   ├── task.py      # Task dataclass + enums
│   │   └── database.py  # Schema and connection management
│   └── services/
│       ├── user_service.py  # User operations
│       └── task_service.py  # Task operations
├── requirements.txt
└── .env.example
```

## Setup

1. **Create a bot** via [@BotFather](https://t.me/BotFather) and copy the token.

2. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and set BOT_TOKEN
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

## Commands

| Command  | Description                  |
|----------|------------------------------|
| `/start` | Register and open main menu  |
| `/help`  | Show available commands      |
| `/tasks` | List your tasks              |
| `/add`   | Start task creation flow     |
| `/stats` | View your task statistics    |

## Tech Stack

- Python 3.10+
- python-telegram-bot 20.x (async)
- aiosqlite (async SQLite)
- python-dotenv (configuration)
