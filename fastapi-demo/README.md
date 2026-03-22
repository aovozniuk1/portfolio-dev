# Task Management REST API

A production-style REST API built with FastAPI, SQLAlchemy, and Alembic for managing users and tasks.

## Features

- **Full CRUD** for Users and Tasks with proper HTTP status codes
- **Relationships** — Users own Tasks (one-to-many with cascade delete)
- **Authentication** — API key validation via `X-API-Key` header
- **JWT Support** — Token generation and verification utilities included
- **Pagination** — `limit`/`offset` on all list endpoints
- **Filtering & Sorting** — Filter tasks by status, priority, owner; sort by multiple fields
- **Validation** — Pydantic v2 schemas with field constraints
- **Error Handling** — Custom exception classes with structured JSON responses
- **Middleware** — CORS and request logging
- **Migrations** — Alembic setup with initial migration
- **Tests** — pytest test suite with 7 test cases using TestClient

## Architecture

```
fastapi-demo/
├── main.py                # CLI entry (uvicorn runner)
├── alembic.ini            # Alembic configuration
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_tables.py
├── app/
│   ├── main.py            # FastAPI app factory
│   ├── core/
│   │   ├── config.py      # pydantic-settings configuration
│   │   ├── security.py    # API key + JWT utilities
│   │   └── exceptions.py  # Custom exception handlers
│   ├── db/
│   │   ├── base.py        # SQLAlchemy declarative base
│   │   └── session.py     # Engine and session factory
│   ├── models/
│   │   ├── user.py        # User ORM model
│   │   └── task.py        # Task ORM model
│   ├── schemas/
│   │   ├── user.py        # User request/response schemas
│   │   ├── task.py        # Task request/response schemas
│   │   └── common.py      # Shared schemas (pagination, health)
│   ├── services/
│   │   ├── user_service.py
│   │   └── task_service.py
│   └── api/v1/
│       ├── router.py      # Aggregated v1 router
│       └── endpoints/
│           ├── users.py
│           ├── tasks.py
│           └── health.py
├── tests/
│   ├── conftest.py        # Fixtures and test DB setup
│   └── test_api.py        # Integration tests
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
# Start the development server
python main.py

# Or directly with uvicorn
uvicorn app.main:app --reload
```

API docs available at: `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint               | Description            | Auth |
|--------|------------------------|------------------------|------|
| GET    | `/api/v1/health`       | Health check           | No   |
| POST   | `/api/v1/users/`       | Create user            | Yes  |
| GET    | `/api/v1/users/`       | List users (paginated) | Yes  |
| GET    | `/api/v1/users/{id}`   | Get user               | Yes  |
| PATCH  | `/api/v1/users/{id}`   | Update user            | Yes  |
| DELETE | `/api/v1/users/{id}`   | Delete user            | Yes  |
| POST   | `/api/v1/tasks/`       | Create task            | Yes  |
| GET    | `/api/v1/tasks/`       | List tasks (paginated) | Yes  |
| GET    | `/api/v1/tasks/{id}`   | Get task               | Yes  |
| PATCH  | `/api/v1/tasks/{id}`   | Update task            | Yes  |
| DELETE | `/api/v1/tasks/{id}`   | Delete task            | Yes  |

## Authentication

Include the API key in the request header:
```
X-API-Key: dev-api-key-change-in-production
```

## Testing

```bash
pytest tests/ -v
```

## Tech Stack

- Python 3.10+
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (sync, SQLite)
- Alembic (migrations)
- Pydantic v2 (validation)
- python-jose (JWT)
- pytest (testing)
