# Tisket — Project Handover

**Status:** Complete and live

**Last verified:** 2026-09-29

## Live services

- **Application:** https://tisket-sepia.vercel.app
- **API health:** https://tisket-api.onrender.com/health
- **API documentation:** https://tisket-api.onrender.com/docs

The API health endpoint returned `status: ok` and `database: ok`. The frontend returned HTTP 200.
The app uses a shared workspace with no login; do not store private information in it.

## What the app does

Tisket is a responsive task and notes app. It supports quick to-dos, task status and priority,
due dates, tags, Markdown notes, pinning, task-linked notes, search across tasks and notes, overdue
and upcoming views, and in-app due-task notifications.

## Stack and deployment

- **Frontend:** React, TypeScript and Vite on Vercel (`frontend/`).
- **API:** Python 3.12, FastAPI, SQLAlchemy and Alembic on Render (`backend/`).
- **Database:** PostgreSQL on Neon.
- **CI:** GitHub Actions runs SQLite and PostgreSQL backend tests, frontend checks, and Playwright E2E.

The Render Blueprint is `render.yaml`; the API container runs migrations before starting the server.
Deployment settings are stored in the hosting dashboards. Never add database URLs, credentials, or
tokens to the repository.

### Hosting notes

- The Render Free web service may sleep after inactivity, so its first request can take about a minute.
- Neon Free has monthly compute and storage limits. Monitor usage in the Neon dashboard.
- All visitors share the same tasks and notes; there is no authentication or per-user data separation.

## Run locally

Prerequisites: Python 3.12, `uv`, Node.js 20+, and npm.

```sh
cd backend
uv sync
cp .env.example .env
```

For a local SQLite workspace, set `DATABASE_URL=sqlite:///./tisket.db` in `backend/.env`. Then run:

```sh
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

In a second terminal:

```sh
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

The local frontend is at `http://localhost:5173`; the API is at `http://localhost:8000` and its docs
are at `http://localhost:8000/docs`.

## Verification

Run backend checks from `backend/`:

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy app
uv run pytest
```

Run frontend checks from `frontend/`:

```sh
npm run lint
npm run format:check
npm run typecheck
npm test
npm run build
npx playwright install chromium  # one-time setup
npm run e2e
```

Last full local run: SQLite backend 187 passed / 2 skipped; PostgreSQL backend 189 passed; frontend
36 passed; Playwright 3 passed. CI passed for deployment commit `787193e`.

## Repository guide

`AGENTS.md` is the authoritative reference for architecture, conventions, environment variables,
commands, and deployment configuration. `README.md` is the user-facing overview and live entry point.
