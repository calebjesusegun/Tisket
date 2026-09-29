# AGENTS.md — Tisket

This file is the single source of truth for anyone (human or AI agent) working on Tisket.
Keep it updated whenever a command, convention, or decision changes.

## 1. Project overview

Tisket is a ToDo, Tasks and Notes web app with one shared workspace (no login: everyone who
opens the app sees and edits the same data).

Features:

- **ToDo & Tasks** — create, edit, delete, complete; priority (low/medium/high); status
  (todo/in_progress/done); optional due date and time; filter by status, priority, tag; sort by
  due date or priority. The ToDo page is a fast checklist view; the Tasks page is the full
  management view. Both use the same `Task` entity (see decisions log).
- **Notes** — create, edit, delete, Markdown with live preview, pin, optional link to a task.
- **Tags** — created on the fly, many tags per task/note, filter by tag.
- **Search** — one box that searches tasks and notes and highlights the matching text
  (PostgreSQL full-text search in production, a `LIKE` fallback on SQLite in tests).
- **Reminders** — due date/time on tasks, overdue highlighting, a "Due soon" view (next 48 h),
  and in-app notifications for tasks that are due (no email).

## 2. Stack and why

| Layer | Choice | Why |
| --- | --- | --- |
| API language | Python 3.12 | Mature typing, fast enough, great ecosystem for web + testing. |
| API framework | FastAPI | Typed request/response models, dependency injection via `Depends`, automatic OpenAPI docs at `/docs`. |
| ORM | SQLAlchemy 2.0 | Typed `Mapped[]` models, works on both PostgreSQL and SQLite, so tests can run in memory. |
| Migrations | Alembic | Standard for SQLAlchemy; versioned, reviewable schema changes. |
| Validation / DTOs | Pydantic v2 | Fast validation, clear error messages, used for request/response schemas and settings. |
| Database | PostgreSQL 16 (prod), SQLite in-memory (unit tests) | PostgreSQL gives full-text search and reliability; SQLite keeps local tests fast. A CI job runs the full suite on PostgreSQL to catch dialect differences. |
| Python tooling | uv, ruff, mypy | uv installs Python 3.12 and locks deps quickly; ruff lints and formats; mypy type-checks. |
| Frontend | React 19 + Vite + TypeScript | Fast dev server and builds, type safety end to end. |
| Server state | TanStack Query | Caching, background refetch, optimistic updates. |
| Routing | React Router | Standard client-side routing. |
| Styling | Tailwind CSS v4 | Utility-first, small CSS output, easy responsive design. |
| Forms | React Hook Form + Zod | Performant, keyboard-friendly forms with schema validation shared by types. |
| Markdown | react-markdown + remark-gfm | Renders Markdown safely (no raw HTML) for note previews. |
| API tests | pytest + httpx (FastAPI `TestClient`) + pytest-cov | Fast, readable tests with coverage gate (≥ 80 %). |
| UI tests | Vitest + React Testing Library + MSW | Vite-native test runner; MSW mocks HTTP at the network layer so hooks are tested realistically. |
| E2E tests | Playwright | Reliable cross-browser flows run against the real backend. |
| Hosting | Vercel (frontend), Railway (API + PostgreSQL) | Git-based deploys, managed PostgreSQL, simple env var management. |
| Frontend tooling | oxlint, Prettier | oxlint ships with the current Vite template, is very fast, and includes the react-hooks and jsx-a11y rules we need. |
| CI | GitHub Actions | Runs lint, type-check, unit, PostgreSQL and E2E tests on every push. |

## 3. Folder structure

```
Tisket/
├── AGENTS.md                  # this file
├── README.md                  # user-facing overview, screenshots, live links
├── .github/workflows/ci.yml   # CI: backend (sqlite + postgres), frontend, e2e
├── backend/
│   ├── pyproject.toml         # deps + ruff/mypy/pytest/coverage config
│   ├── uv.lock
│   ├── alembic.ini
│   ├── alembic/               # env.py + versions/ (migrations)
│   ├── Dockerfile             # production image; runs migrations on start
│   ├── railway.json           # Railway build/deploy config
│   ├── .env.example           # env var names (no secrets)
│   ├── app/
│   │   ├── main.py            # create_app() app factory + module-level `app`
│   │   ├── core/              # config (pydantic-settings), errors, clock
│   │   ├── db/                # engine/session factory, Base, custom column types
│   │   ├── models/            # SQLAlchemy models (Task, Note, Tag, association tables)
│   │   ├── schemas/           # Pydantic DTOs (request/response), kept separate from models
│   │   ├── repositories/      # all database queries live here
│   │   ├── services/          # business rules (tasks, notes, tags, search, reminders)
│   │   ├── routers/           # thin HTTP layer, one module per resource
│   │   └── dependencies.py    # FastAPI Depends providers (session, repos, services)
│   └── tests/                 # pytest; api/ (endpoint tests) and services/ (unit tests)
└── frontend/
    ├── package.json
    ├── vite.config.ts         # Vite + Vitest config
    ├── playwright.config.ts   # E2E config (starts backend + frontend)
    ├── vercel.json            # SPA rewrites for Vercel
    ├── .env.example
    ├── e2e/                   # Playwright specs
    └── src/
        ├── app/               # App root, router, providers, layout, error boundary
        ├── lib/               # api client (typed fetch wrapper), query client, utils
        ├── components/        # small reusable presentational components (Button, Badge…)
        ├── features/
        │   ├── tasks/         # api.ts, hooks.ts, components/, pages/
        │   ├── notes/
        │   ├── tags/
        │   ├── search/
        │   └── reminders/
        └── test/              # test setup, MSW handlers, render helpers
```

## 4. Design patterns and where they are used

### Backend

| Pattern | Where |
| --- | --- |
| Layered architecture | `routers/` → `services/` → `repositories/` → `models/`. Routers never touch the session directly. |
| Repository pattern | `app/repositories/*.py` — every SQLAlchemy query lives here (`TaskRepository`, `NoteRepository`, `TagRepository`, `SearchRepository`). |
| Service layer | `app/services/*.py` — business rules: tag normalisation and get-or-create (`TagService`), completion timestamps (`TaskService`), reminder windows / overdue / notifications (`ReminderService`), search highlighting (`SearchService`). |
| Dependency injection | `app/dependencies.py` — `get_db` yields a session; `get_*_service` build services with their repositories and the injectable `Clock`. Tests override `get_db` and `get_clock`. |
| DTOs | `app/schemas/*.py` — Pydantic models for input/output; ORM models are never returned directly. |
| App factory | `app/main.py::create_app(settings)` — tests build a fresh app per test with their own settings. |
| Centralised error handling | `app/core/errors.py` — `AppError` subclasses + exception handlers produce `{"error": {"code", "message", "details"}}` for every error, including validation errors and 404/405. |
| Settings from env | `app/core/config.py` — `Settings(BaseSettings)` reads env vars / `.env`. |

### Frontend

| Pattern | Where |
| --- | --- |
| Feature-based folders | `src/features/{tasks,notes,tags,search,reminders}` each own their API calls, hooks, components and pages. |
| Single typed API client | `src/lib/api-client.ts` — one `request<T>()` wrapper that sets headers, parses JSON, and throws `ApiError` with the backend error shape. Feature `api.ts` files call it. |
| Custom hooks wrapping TanStack Query | `features/*/hooks.ts` — e.g. `useTasks`, `useUpdateTask`, `useNotes`, `useSearch`, `useDueSoon`, `useNotifications`. |
| Optimistic updates | `useToggleTaskComplete` in `features/tasks/hooks.ts` updates cached lists before the server responds and rolls back on error. |
| Container / presentational split | `*Container.tsx` / pages fetch data via hooks; presentational components (`TaskItem`, `NoteCard`, `TagChip`, …) only receive props. |
| Error boundary, loading & empty states | `src/app/ErrorBoundary.tsx`, `components/LoadingState.tsx`, `components/EmptyState.tsx`, `components/ErrorState.tsx`. |

## 5. Coding conventions

- **Python**: ruff (lint + format, line length 100), mypy on `app/`. Type-hint everything.
  Routers stay thin: parse input → call service → return schema. Raise `AppError` subclasses
  (`NotFoundError`, `ConflictError`, `BadRequestError`), never `HTTPException`, from services.
- **Datetimes**: always timezone-aware UTC in the API and DB (`UTCDateTime` column type).
  The frontend converts to local time for display.
- **API**: JSON, snake_case fields, plural resource names, under `/api/v1`. List endpoints return
  `{"items", "total", "page", "page_size", "pages"}` and accept `page` (≥1) and `page_size` (1–100).
- **TypeScript**: strict mode (+ `noUncheckedIndexedAccess`), oxlint + Prettier. No `any`. Components are function components;
  file names `PascalCase.tsx` for components, `camelCase.ts` otherwise.
- **Styling**: Tailwind utilities only; shared look lives in `src/components`.
- **Tests**: written with each feature. Never delete or weaken a test to make it pass; fix the cause.
- **Commits**: small, imperative mood (`Add tasks API`), one concern per commit.
- **Secrets**: never committed — not even throwaway ones. Only `.env.example` files with names are in git.
  CI databases use passwordless `trust` auth; real credentials live only in Railway/Vercel/GitHub
  secrets settings.

## 6. Commands

All commands are run from the repository root unless stated. Prerequisites: `uv`
(`brew install uv`), Node 20+ and npm, and for local PostgreSQL: `brew install postgresql@16`.

### Backend (`cd backend`)

| Task | Command |
| --- | --- |
| Install (also installs Python 3.12) | `uv sync` |
| Configure env | `cp .env.example .env` then edit `DATABASE_URL` |
| Run migrations | `uv run alembic upgrade head` |
| Run dev server (http://localhost:8000, docs at /docs) | `uv run uvicorn app.main:app --reload` |
| Run tests (SQLite in memory, with coverage ≥ 80 %) | `uv run pytest` |
| Run tests against PostgreSQL | `TEST_DATABASE_URL=postgresql+psycopg://USER@localhost:5432/tisket_test uv run pytest` |
| Lint | `uv run ruff check .` |
| Format check / format | `uv run ruff format --check .` / `uv run ruff format .` |
| Type-check | `uv run mypy app` |
| New migration | `uv run alembic revision --autogenerate -m "describe change"` |
| Roll back one migration | `uv run alembic downgrade -1` |

Local PostgreSQL (one-time):

```bash
export LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8   # macOS: postgres refuses to start without a valid locale
/opt/homebrew/opt/postgresql@16/bin/initdb -D ~/.tisket-pg -U postgres --auth=trust --locale=en_US.UTF-8
/opt/homebrew/opt/postgresql@16/bin/pg_ctl -D ~/.tisket-pg -l ~/.tisket-pg/log start
createdb -h localhost -U postgres tisket
createdb -h localhost -U postgres tisket_test
```

### Frontend (`cd frontend`)

| Task | Command |
| --- | --- |
| Install | `npm ci` |
| Configure env | `cp .env.example .env.local` (defaults to `http://localhost:8000`) |
| Run dev server (http://localhost:5173) | `npm run dev` |
| Unit/component tests | `npm test` |
| Tests with coverage | `npm run test:coverage` |
| Lint | `npm run lint` |
| Format check / format | `npm run format:check` / `npm run format` |
| Type-check | `npm run typecheck` |
| Production build | `npm run build` |
| Install Playwright browser (one-time) | `npx playwright install chromium` |
| E2E tests (starts backend on :8001 with a fresh SQLite file DB and frontend on :4173) | `npm run e2e` |

## 7. Migrations

- Models live in `backend/app/models`. After changing them, run
  `uv run alembic revision --autogenerate -m "..."`, review the generated file, and commit it.
- PostgreSQL-only objects (the full-text GIN indexes) are created inside
  `if op.get_bind().dialect.name == "postgresql"` blocks so migrations also run on SQLite.
  Their names are listed in `app/db/manual_indexes.py` so autogenerate does not try to drop them.
- `tests/unit/test_migrations.py` fails if the migrated schema drifts from the models, so a
  forgotten migration is caught in CI (on SQLite and on PostgreSQL).
- Migrations run automatically on deploy: the Docker `CMD` runs `alembic upgrade head` before
  starting uvicorn.

## 8. Environment variables (names only)

Backend:

| Name | Purpose | Example value shape |
| --- | --- | --- |
| `APP_ENV` | `development`, `test` or `production` | `production` |
| `DATABASE_URL` | SQLAlchemy URL. `postgres://` / `postgresql://` are rewritten to `postgresql+psycopg://` automatically. | `postgresql://user:pass@host:5432/db` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins. In production set it to the Vercel URL only. | `https://tisket.vercel.app` |
| `PORT` | Port uvicorn binds to (set by Railway). | `8000` |
| `TEST_DATABASE_URL` | Tests only: run the suite against PostgreSQL instead of SQLite. | — |

Frontend:

| Name | Purpose |
| --- | --- |
| `VITE_API_URL` | Base URL of the backend (no trailing slash), e.g. the Railway URL. |

## 9. Testing approach

- **Backend unit/API tests** (`backend/tests`): each test gets a fresh app from `create_app()`
  and a fresh in-memory SQLite database (`StaticPool`). `get_clock` is overridden with a fixed
  clock so reminder logic is deterministic. Every endpoint has success and failure tests;
  services for reminders and tags have direct unit tests. Coverage gate: `--cov-fail-under=80`.
- **PostgreSQL run**: when `TEST_DATABASE_URL` is set, the suite runs Alembic migrations against
  that database once and truncates tables between tests. CI runs this on a PostgreSQL 16 service,
  which exercises the real full-text search path and the migrations.
- **Frontend tests** (`frontend/src/**/*.test.tsx`): Vitest + React Testing Library with MSW
  handlers in `src/test/`. Cover the API client, key hooks (including the optimistic update),
  and key components/pages.
- **E2E** (`frontend/e2e`): Playwright starts the real backend (fresh SQLite file DB, migrated with
  Alembic) and a production build of the frontend. Flows: create a task, create a note with tags,
  search. Configuration lives in `frontend/playwright.config.ts`; the database file is unique per
  Playwright run and stored under `/tmp` so E2E runs start from an empty workspace. CI installs
  Chromium and runs `npm run e2e` in a separate job.

## 10. Deployment

Backend + database on Railway:

1. Railway → New Project → Deploy from GitHub repo → select this repo.
2. In the service settings set **Root Directory** to `backend` (Railway then uses
   `backend/railway.json` and `backend/Dockerfile`).
3. Add a PostgreSQL database to the project. In the backend service variables add
   `DATABASE_URL=${{Postgres.DATABASE_URL}}`, `APP_ENV=production`,
   `ALLOWED_ORIGINS=https://<your-vercel-domain>`.
4. Settings → Networking → Generate Domain. Health check path is `/health`.
5. Every deploy runs `alembic upgrade head` before starting the server.

Frontend on Vercel:

1. Vercel → Add New Project → import this repo, **Root Directory** `frontend`
   (framework preset: Vite; `frontend/vercel.json` adds SPA rewrites).
2. Add env var `VITE_API_URL=https://<your-railway-domain>` and deploy.
3. Put the final Vercel domain into Railway's `ALLOWED_ORIGINS` and redeploy the backend.

## 11. Decisions log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-09-29 | ToDo and Tasks share one `Task` model; the ToDo page is a quick checklist view and the Tasks page is the full management view. | One source of truth, no duplicated logic; a todo item is a task with only a title. |
| 2026-09-29 | Use `uv` to install Python 3.12 and manage dependencies. | Machine had Python 3.9 only; uv pins 3.12, is fast, and produces a lockfile. Tooling, not a stack change. |
| 2026-09-29 | Synchronous SQLAlchemy with `psycopg` (v3) driver. | FastAPI runs sync endpoints in a thread pool; sync code is simpler to test and fast enough for this app. |
| 2026-09-29 | Enums stored as strings with CHECK constraints (`native_enum=False`). | Same schema on PostgreSQL and SQLite; adding values later does not need `ALTER TYPE`. |
| 2026-09-29 | Search highlights returned as structured segments `[{"text", "match"}]`, not HTML. | The UI renders `<mark>` itself, so no `dangerouslySetInnerHTML` and no XSS risk. PostgreSQL uses `ts_headline` with private-use delimiter characters, SQLite uses a case-insensitive regex. |
| 2026-09-29 | Tag names normalised (trimmed, lower-case, internal whitespace → `-`, max 30 chars) and unique. | "Work", " work " and "WORK" are the same tag; avoids duplicates when tags are created on the fly. |
| 2026-09-29 | Notifications = tasks that are due (due time ≤ now), not done, and not dismissed since they became due. Dismissal is stored on the task (`reminder_dismissed_at`). | Shared workspace has no users, so dismissal is global; the frontend polls every 60 s. |
| 2026-09-29 | Migrations run in the container start command. | Guarantees schema is current before the app serves traffic on every Railway deploy. |
| 2026-09-29 | oxlint instead of ESLint for the frontend. | It is the Vite template default, runs in milliseconds, and covers react-hooks, jsx-a11y and TypeScript rules. |
| 2026-09-29 | SQLAlchemy pinned to `>=2.0.40,<2.1`. | The brief specifies SQLAlchemy 2.0; uv would otherwise resolve 2.1. |
| 2026-09-29 | CI PostgreSQL service uses `POSTGRES_HOST_AUTH_METHOD: trust` with no password. | Keeps every credential, even disposable ones, out of the repository. |
| 2026-09-29 | Search uses prefix matching (`to_tsquery('english', 'term:*' & …)`), all terms required; title weighted A, body B. | Search-as-you-type finds "groceries" from "groc"; title hits rank first, matching the SQLite fallback. Terms are reduced to `\w+` words, so users cannot inject tsquery operators. |
| 2026-09-29 | The tsvector expression is emitted as literal SQL (not bound params) and a PostgreSQL test runs `EXPLAIN` to assert the GIN index is used. | Parameterised expressions would not match the index expression, silently causing sequential scans. |
| 2026-09-29 | Reminders are three paginated endpoints (`/reminders/due-soon`, `/overdue`, `/notifications`) plus `POST /{id}/dismiss` and `/dismiss-all`. | Keeps every list endpoint paginated and lets the UI fetch each section independently. |
| 2026-09-29 | The initial migration's FTS index was edited in place (weights added) before the first deploy. | No database outside local dev/CI had applied it; after deploy, schema changes must be new migrations. |
| 2026-09-29 | MSW for frontend HTTP mocking. | Tests hooks and pages through the real API client instead of mocking modules. |
