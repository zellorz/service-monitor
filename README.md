# Service Monitor

Scheduled health checks for websites and APIs, with history and alerts.

> 🚧 Work in progress.

## Stack

Python 3.12 · FastAPI · Pydantic · Docker · uv · pytest · Ruff

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

API docs at http://localhost:8000/docs

## Development

```bash
uv sync
uv run fastapi dev src/service_monitor/main.py
uv run pytest
uv run ruff check .
```