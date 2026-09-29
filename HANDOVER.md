# HANDOVER — continue building Tisket

> **Paste this whole file to the next AI agent (e.g. Gemini) as its first message**, or tell it:
> "Read `HANDOVER.md` and `AGENTS.md` in the repo root and continue from the first unfinished phase."
> The previous agent (Claude) keeps the **Progress** section below updated after every phase, so it is
> accurate even if work stopped mid-phase.

---

> ### ▶ RESUME HERE (last updated 2026-09-29, after Phase 6)
> - **Phases 1–6 are done**, pending commit/push and CI verification for Phase 6.
> - **Next: Phase 7 (Playwright E2E).** Add the three planned browser flows and an E2E job to CI.
> - Phase 6 frontend verification: lint, formatting, typecheck, build passed; 36 tests passed.
>   The production build emits a chunk size advisory for its 650 kB JavaScript bundle.
> - Backend baseline remains 187 SQLite tests (96.7 % coverage) and 189 PostgreSQL tests.

## 0. Your job

You are continuing the implementation of **Tisket**, a ToDo, Tasks and Notes web app, in the repo at
`[local-path]
branch `main`). Earlier phases are done and committed. Find the resume point (section 2), then keep
going phase by phase until Phase 9 is complete.

Read these first, in order:

1. `AGENTS.md`: stack, folder structure, patterns, conventions, commands, and the decisions log.
   It is binding. Keep it updated as you work.
2. This file, especially **Progress** (section 2) and **Plan for remaining phases** (section 4).
3. `git log --oneline` and `git status`, to confirm where work actually stopped.

## 1. The original brief (from the user, verbatim requirements)

**Goal.** A publicly deployed web app with three parts: a ToDo list, task management, and a Notes
feature. Two extra features: (1) tags with a single search box that searches across tasks and notes,
and (2) reminders with due dates, overdue highlighting and a "due soon" view. No login: everyone shares
one workspace.

**Stack (fixed; do not change without recording the reason in AGENTS.md).**
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PostgreSQL in production.
- Local tests: SQLite in memory. CI also runs the suite once against PostgreSQL.
- Frontend: React + Vite + TypeScript, TanStack Query, React Router, Tailwind CSS, React Hook Form + Zod.
- Testing: pytest + httpx (API), Vitest + React Testing Library (UI), Playwright for 2–3 E2E flows.
- Deployment: frontend on Vercel; backend and PostgreSQL on Railway. GitHub Actions runs all tests on
  every push.

**Backend patterns.** Layered architecture (routers → services → repositories → models); repository
pattern; service layer for business rules (reminders, tags); DI via FastAPI `Depends`; Pydantic DTOs
separate from models; app factory; centralised JSON error handling; settings via pydantic-settings.

**Frontend patterns.** Feature folders (tasks, notes, tags, search, reminders); a single typed API
client; custom hooks per feature wrapping TanStack Query; optimistic update when completing a task;
small reusable components; container vs presentational split; an error boundary; clear loading and
empty states.

**Features.**
- Tasks/ToDo: create, edit, delete, mark complete, priority (low/medium/high), status
  (todo/in_progress/done), optional due date, filter by status/priority/tag, sort by due date or priority.
- Notes: create, edit, delete, simple Markdown with preview, pin, optional link to a task.
- Tags: created on the fly, several per task/note, filter by tag.
- Search: one box, returns matching tasks and notes with the matching text highlighted.
  PostgreSQL full-text search in production, a simple fallback on SQLite.
- Reminders: due date and time on tasks, overdue highlighted, "Due soon" view (next 48 h), in-app
  notifications for due items. No email.
- Responsive (works on a phone), keyboard-friendly forms, clean simple design.

**API.** REST under `/api/v1` for tasks, notes, tags, search, reminders. Pagination on list endpoints.
Clear validation errors. `/health`. OpenAPI at `/docs`. CORS limited to the Vercel domain in production.

**Testing.** Write tests with each feature, not at the end. Cover every endpoint (success and failure
cases), service logic for reminders and tags, key UI components and hooks, and E2E flows for creating
a task, creating a note with tags, and searching. Backend coverage ≥ 80 %. **Run the full suite and show
passing output before calling any phase done.** If a test fails, fix the cause. Never delete or weaken
a test to make it pass.

**Deployment.** Backend Dockerfile, Railway config, Vercel config. Env vars for the database URL and the
allowed frontend origin. Migrations run automatically on backend deploy. Deploy both, then confirm the
live app works by creating a task and a note on the public URL. Give the user both public URLs and a
short checklist of anything they must click or paste themselves in Vercel or Railway.

**Phases.**
1. AGENTS.md, repo, folders, linting, CI.
2. Backend foundation: models, migrations, app factory, health check, first tests.
3. Tasks and tags API with tests.
4. Notes, search and reminders API with tests.
5. Frontend foundation: routing, API client, layout, TanStack Query setup.
6. Frontend features: tasks, notes, tags, search, reminders, with tests.
7. End-to-end tests with Playwright.
8. Deployment and live verification.
9. Final review: run all tests, verify every command in AGENTS.md from a clean state, update the
   README with screenshots and live links.

**Rules.**
- Ask the user before any decision that changes the stack or the scope.
- **Never commit secrets, not even throwaway ones.** The user rejected a committed CI Postgres
  password, so CI uses `POSTGRES_HOST_AUTH_METHOD: trust`. Before every commit, grep for
  `password|secret|token|api_key` and URLs that embed credentials.
- Keep commits small. After each phase, commit with a clear message and end the commit message with
  `Co-Authored-By:` for the agent if applicable. Push to `origin main` and check CI
  (`gh run list -L1`, `gh run watch <id>`).
- At the end of each phase, give the user a two or three sentence summary of what works and what
  is next.
- **Update section 2 (Progress) of this file at the end of every phase.**

## 2. Progress (keep this current)

| Phase | Status | Notes |
| --- | --- | --- |
| 1. AGENTS.md, repo, lint, CI | ✅ done | CI has 3 jobs: backend SQLite, backend PostgreSQL, frontend. |
| 2. Backend foundation | ✅ done | Models, initial migration (with PG GIN FTS indexes), app factory, errors, CORS, `/health`, 25 tests, 96 % coverage, green on SQLite and PostgreSQL. |
| 3. Tasks + tags API | ✅ done | `/api/v1/tasks` (filters: repeatable `status`, `priority`, `tag`; sort `due_at`/`priority`/`created_at`/`updated_at`/`title`) and `/api/v1/tags`. Services: `TagService`, `TaskService`, pure `services/reminder_rules.py` (is_overdue, is_due_soon, needs_notification). 121 tests, 98.6 % coverage; green on PostgreSQL. Test helpers are in `tests/factories.py`. Service list methods are named `list_tasks` and `list_tags`, and the repo uses `find`, to avoid shadowing `list`. |
| 4. Notes, search, reminders API | ✅ done | `/api/v1/notes` (filters tag/pinned/task_id, pinned first), `/api/v1/search?q=&type=all|task|note` (segments in `title_highlights` and `snippet`), `/api/v1/reminders/{due-soon?hours=,overdue,notifications}` (all `Page[TaskRead]`), `POST /reminders/{id}/dismiss` → TaskRead, `POST /reminders/dismiss-all` → `{dismissed}`. 187 tests on SQLite (96.7 %), 189 on PG, including an EXPLAIN check that the GIN index is used. **The backend API is complete.** |
| 5. Frontend foundation | ✅ done | See "Frontend foundation reference" below. |
| 6. Frontend features | ✅ done | Implemented task/ToDo, notes, tags, search and reminders pages, hooks and components. Optimistic task completion; 36 frontend tests. Lint, format, typecheck, tests and build pass. |
| 7. Playwright E2E | ⬜ | Add an `e2e` job to CI in this phase. |
| 8. Deployment | ⬜ | Railway and Vercel CLIs are installed but **not logged in**; the user must log in or connect the repo in the dashboards. |
| 9. Final review + README | ⬜ | |

### Frontend foundation reference (Phase 5, done)

- `src/lib/`:
  - `api-client.ts`: `request<T>(path, {method, body, query, signal})`, `ApiError` and
    `errorMessage`.
  - `types.ts`: API types.
  - `query-client.ts`: `createQueryClient()`.
  - `format.ts`: `toLocalInput`/`fromLocalInput` for `datetime-local`, plus `formatRelative` and
    `formatDateTime`.
- `src/components/`:
  - `Button`, `TextInput`/`TextArea`/`SelectInput` (these take `ref`, so RHF `register` works),
    `Badge`, `LoadingState`/`EmptyState`/`ErrorState`, `Modal`, and icons.
  - Toasts: `ToastProvider` plus `useToast()` from `components/toast-context.ts`.
- `src/app/`:
  - `routes.tsx` still uses `PlaceholderPage` for every page, and **Phase 6 replaces them** with
    real pages.
  - `Layout` takes a `headerActions` prop for the NotificationBell.
  - `nav.ts` holds `NAV_ITEMS`.
- Tests: `src/test/`
  - `server.ts`: MSW. `setup.ts` starts it with `onUnhandledRequest: 'error'`.
  - `handlers.ts`: `API` constant plus empty-workspace defaults. Override per test with
    `server.use(...)`.
  - `factories.ts`: `makeTask`, `makeNote`, `makeTag`, `page()`.
  - `utils.tsx`: `renderRoute({route})` renders the real routes, and
    `renderWithProviders(ui, {route})`.
  - `createTestQueryClient()` sets retry to false.
- Test files for Button and friends live in `src/components/components.test.tsx`. Layout,
  ErrorBoundary, the api-client and format are covered too (28 tests in total).
- Oxlint: `jsx-a11y/prefer-tag-over-role` is off, `only-export-components` is off for test files, and
  `vi.fn` needs type params (`vi.fn<() => void>()`).
- Local dev servers: `.claude/launch.json` (git-ignored) has `backend` (port 8000, local PG `tisket`
  DB) and `frontend` (port 5173).

**To find the exact resume point:** a phase whose code exists but isn't marked ✅ may be half done.
Run the test suites (section 3). Anything missing from the section 4 plan for that phase is still to
do, including its tests.

## 3. Environment facts (the user's Mac)

- `uv` is installed via Homebrew. Python 3.12 is managed by uv (system Python is 3.9, so don't use it).
  Always run Python through `uv run …` inside `backend/`.
- Node 24 and npm 11 are available. Docker is **not** installed.
- Local PostgreSQL 16 lives at `~/.tisket-pg` (trust auth, user `postgres`, databases `tisket` and
  `tisket_test`). If it isn't running, start it with:
  `export LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8; /opt/homebrew/opt/postgresql@16/bin/pg_ctl -D ~/.tisket-pg -l ~/.tisket-pg/log start`
  (without `LC_ALL` it fails with "postmaster became multithreaded").
- `gh` is logged in as `[repository-owner]`.
- Verification commands:
  - Backend: `cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app && uv run pytest`
  - Backend on PostgreSQL: `TEST_DATABASE_URL=postgresql+psycopg://postgres@localhost:5432/tisket_test uv run pytest`
  - Frontend: `cd frontend && npm run lint && npm run format:check && npm run typecheck && npm test && npm run build`

## 4. Plan for remaining phases (follow it, since it is consistent with the code already written)

### Existing backend building blocks (Phase 2)
- `app/main.py::create_app(settings)` stores `engine` and `session_factory` on `app.state`, and adds
  CORS and error handlers. Routers are included here, so add each new router with
  `prefix=API_PREFIX` (`/api/v1`).
- `app/dependencies.py` provides `DbSession`, `ClockDep` (injectable `Clock`, where tests use `FixedClock`
  at 2026-01-15 12:00 UTC), and `PageParamsDep` (`page`, `page_size` ≤ 100). Add `get_*_repository` and
  `get_*_service` providers here.
- `app/core/errors.py` has `NotFoundError`, `ConflictError` and `BadRequestError`, which services raise.
  All errors come back as `{"error": {"code", "message", "details"}}`.
- `app/schemas/common.py` has `Page[T].build(items, total, page, page_size)`.
- Models: `Task` (title ≤ 200, description, status, priority, due_at, completed_at,
  reminder_dismissed_at, created_at, updated_at, tags, notes); `Note` (title, content, pinned, task_id
  FK with SET NULL, tags, task); `Tag` (name unique ≤ 30). Enums use string values
  (`todo|in_progress|done`, `low|medium|high`). `PRIORITY_RANK` is in `app/models/enums.py`.
  Datetimes use `UTCDateTime` (always timezone-aware UTC).
- Test fixtures (`tests/conftest.py`): `client`, `app`, `db`, `clock` (FixedClock with `.advance()`
  and `.set()`), `settings`. Put API tests in `tests/api/` and service unit tests in `tests/services/`.

### Phase 3: Tasks and tags API
- `app/services/tag_service.py` `TagService`:
  - `normalize(name)`: strip, lower-case, collapse internal whitespace to `-`.
  - Validate: 1–30 characters, `[a-z0-9-_]` only. Otherwise raise `BadRequestError` with details.
  - `resolve(names) -> list[Tag]`: normalises and de-duplicates, then gets or creates each tag
    (created on the fly).
  - Also `list`, `create`, `rename` (ConflictError on duplicate) and `delete`.
- `app/repositories/tag_repository.py`: `get`, `get_by_name(s)`, `add`, `list_with_counts`
  (task_count and note_count via subqueries), `delete`.
- `app/repositories/task_repository.py`: `get`, `add`, `delete`, and
  `list(filters, sort, order, page)`. Filters are `status`, `priority`, `tag` (name), `due_before`,
  `due_after` and `q` (optional). Sort is `due_at` (nulls last), `priority` (CASE on
  `PRIORITY_RANK`), `created_at` or `updated_at`, with order asc or desc and `id` as tiebreak.
  Returns `(items, total)`.
- `app/services/task_service.py`: `create`, `update` (partial PATCH via
  `model_dump(exclude_unset=True)`), `delete`, `get`, `list`. Setting status to `done` sets
  `completed_at=clock.now()`, and leaving `done` clears it. Changing `due_at` clears
  `reminder_dismissed_at`. Tags are passed as names and resolved through `TagService`.
- Schemas (`app/schemas/task.py`, `tag.py`):
  - `TaskCreate`: title stripped (1–200), description ≤ 5000, status, priority, due_at (optional; a
    naive value is treated as UTC), tags (list[str], ≤ 10).
  - `TaskUpdate`: every field optional.
  - `TaskRead`: all fields plus `tags: list[TagRead]`, and computed `is_overdue` and `is_due_soon`,
    which the service fills using the clock (due_at < now and not done; within 48 h).
  - `TagRead {id, name}`, `TagWithCounts`, `TagCreate`, `TagUpdate`.
- Routers (`app/routers/tasks.py`, `tags.py`):
  - `GET/POST /api/v1/tasks`, `GET/PATCH/DELETE /api/v1/tasks/{id}` (DELETE → 204).
  - `GET/POST /api/v1/tags`, `PATCH/DELETE /api/v1/tags/{id}`.
  - GET `/tasks` query parameters: `status`, `priority`, `tag`, `sort`, `order`, `page` and
    `page_size`.
- Tests:
  - Every endpoint, success and failure: 404, 422 for a blank title, bad enum or page_size > 100,
    409 for a duplicate tag rename, and 400 for a bad tag name.
  - Filters and sorts, including nulls-last on `due_at`.
  - `completed_at` behaviour and tags created on the fly.
  - Unit tests for `TagService` normalisation and resolve.
  - Everything must pass on SQLite and on PostgreSQL.

### Phase 4: Notes, search and reminders API
- Notes:
  - `NoteRepository` and `NoteService` (`task_id` must exist, otherwise 400 `BadRequestError`).
  - Schemas: `NoteCreate` (title 1–200, content ≤ 20000, pinned, task_id, tags), `NoteUpdate`, and
    `NoteRead` (adds `task: {id, title} | None` and `tags`).
  - `GET /api/v1/notes` filters: `tag`, `pinned`, `task_id`. Order is pinned first, then
    `updated_at` desc. Also GET/PATCH/DELETE on `/notes/{id}`.
  - Deleting a task sets the note's `task_id` to null. The FK already does this, and PRAGMA
    foreign_keys is on in SQLite.
- Search: `GET /api/v1/search?q=&type=all|task|note&page=&page_size=`.
  - `SearchRepository` on PostgreSQL:
    `to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description|content,''))
    @@ websearch_to_tsquery('english', q)`. The expression must match the GIN index in the migration.
    Rank with `ts_rank`. Highlight with `ts_headline(..., 'StartSel=, StopSel=,
    MaxFragments=2, MinWords=5, MaxWords=20, HighlightAll=false')` on title and body.
  - SQLite fallback: every whitespace term must match (case-insensitive `LIKE`) the title or body.
  - `SearchService` turns text into segments `[{"text": str, "match": bool}]`, parsing the
    `/` markers on PostgreSQL and using a case-insensitive regex over the query terms on
    SQLite, plus a snippet around the first match.
  - Result item:
    `{type: "task"|"note", id, title, title_highlights, snippet_highlights, tags, updated_at, status?, pinned?}`.
    Tasks and notes are merged and ordered by rank, then `updated_at`.
  - A blank `q` → 422. Test the highlighting on both engines; assert on `match: true` segments
    loosely, because PostgreSQL stems words.
- Reminders: `ReminderService(repo, clock)`.
  - `GET /api/v1/reminders/due-soon?hours=48` (1–168) returns `{overdue: Page[TaskRead]-like list,
    due_soon: …}`, or two paginated lists. Due soon means not done and `now <= due_at <= now+hours`;
    overdue means not done and `due_at < now`.
  - `GET /api/v1/reminders/notifications` returns the tasks that are due. That is `due_at <= now`,
    not done, and `reminder_dismissed_at` null or `< due_at`. Include a `count`.
  - `POST /api/v1/reminders/{task_id}/dismiss` sets `reminder_dismissed_at = now`, with a 404 if the
    task doesn't exist.
  - Unit-test the service with `FixedClock` (window boundaries, done tasks excluded, and dismissal
    reset when the due date changes).
- Keep backend coverage ≥ 80 %.

### Phase 5: Frontend foundation
- `src/lib/api-client.ts`: `request<T>(path, {method, body, query})` using `import.meta.env.VITE_API_URL`
  (default `http://localhost:8000`) and the `/api/v1` prefix. It throws `ApiError(status, code, message,
  details)` built from the backend error shape. Add `src/lib/types.ts` with TS types that mirror the
  schemas.
- `src/lib/query-client.ts`: QueryClient with sensible defaults (retry 1, staleTime 30 s).
- `src/app/`:
  - `App.tsx` with `QueryClientProvider` and the router.
  - `router.tsx` (React Router v7+ `createBrowserRouter`). Routes: `/` → redirect to `/todo`,
    `/todo`, `/tasks`, `/notes`, `/notes/new`, `/notes/:id`, `/due-soon`, `/search`, `/tags`, and 404.
  - `Layout.tsx`: a sidebar on desktop and a bottom nav on mobile, with a header that has the search
    box and the notification bell.
  - `ErrorBoundary.tsx`.
- `src/components/`: Button, Input, Select, Textarea, Badge, TagChip, EmptyState, LoadingState,
  ErrorState, Modal or Drawer, PriorityBadge, StatusBadge.
- MSW setup in `src/test/` (server, handlers, a `renderWithProviders` helper). Tests for the
  api-client, Layout navigation and the ErrorBoundary.

### Phase 6: Frontend features
Each feature folder has `api.ts`, `hooks.ts`, `components/` and `pages/`.
- Tasks:
  - Hooks: `useTasks(filters)`, `useCreateTask`, `useUpdateTask`, `useDeleteTask`, and
    `useToggleTaskComplete`. The toggle is an **optimistic update**: `onMutate` patches every cached
    `['tasks', …]` list, `onError` rolls back, and `onSettled` invalidates.
  - ToDo page: a quick-add input and a checklist.
  - Tasks page: filter bar (status, priority, tag), sort select, and a list with an edit/create
    form in a modal. The form uses React Hook Form + Zod and has a `datetime-local` input for the
    due date.
  - Overdue rows are highlighted in red.
- Notes:
  - A list with pinned notes first and a tag filter.
  - The editor has tabs for Write and Preview (react-markdown + remark-gfm, no raw HTML).
  - It has a pin toggle, a tag input and a task link select.
- Tags: a `TagInput` component (comma or Enter adds a chip, Backspace removes) and a tags
  management page (rename, delete, counts).
- Search: the header search box navigates to `/search?q=`. The results page renders highlight
  segments with `<mark>`, split into Tasks and Notes groups.
- Reminders:
  - A "Due soon" page with Overdue and Next 48 h sections.
  - `useNotifications` polls every 60 s.
  - A bell in the header shows a badge count and a dropdown with Dismiss buttons.
  - A toast appears when new due items arrive.
- Tests (Vitest + RTL + MSW) for TaskItem, TaskForm validation, `useToggleTaskComplete` (optimistic
  update and rollback), NoteEditor preview, TagInput, search highlighting and the notification bell.

### Phase 7: E2E (Playwright)
- `frontend/playwright.config.ts` uses `webServer`. It starts the backend with a fresh SQLite file
  database (`DATABASE_URL=sqlite:///./e2e.db`, `ALLOWED_ORIGINS=http://localhost:4173`), runs
  `uv run alembic upgrade head`, and then serves uvicorn on port 8001. The frontend runs as
  `npm run build && npm run preview -- --port 4173` with `VITE_API_URL=http://localhost:8001`.
- Specs:
  - `create-task.spec.ts`
  - `note-with-tags.spec.ts`
  - `search.spec.ts`: create a task and a note, search, and check the `<mark>` highlight.
- Add an `e2e` job to `.github/workflows/ci.yml` (setup-uv, setup-node,
  `npx playwright install --with-deps chromium`, `npm run e2e`).

### Phase 8: Deployment
- `backend/Dockerfile`: python:3.12-slim with uv. Install with `uv sync --locked --no-dev`, then
  `CMD sh -c "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"`.
  Add `.dockerignore`.
- `backend/railway.json`: DOCKERFILE builder, healthcheck `/health`, restart on failure.
- `frontend/vercel.json`: SPA rewrite of `/(.*)` → `/index.html`.
- The user must log in to Railway and Vercel (`railway login`, `vercel login`), or connect the GitHub
  repo in each dashboard. Railway: set Root Directory `backend`, add PostgreSQL, and set the vars
  `DATABASE_URL=${{Postgres.DATABASE_URL}}`, `APP_ENV=production` and
  `ALLOWED_ORIGINS=https://<vercel-domain>`. Vercel: Root Directory `frontend` and
  `VITE_API_URL=https://<railway-domain>`.
- Verify live by creating a task and a note through the public UI. Give the user both URLs and the
  click/paste checklist.

### Phase 9: Final review
Run every command in AGENTS.md from a clean clone (`git clone` into a temp dir, then `uv sync`,
`npm ci`, and so on) and fix anything broken. Add screenshots (Playwright can capture them into
`docs/screenshots/`). Write `README.md` with the features, live links, screenshots and a quickstart.
Update AGENTS.md and this file.
