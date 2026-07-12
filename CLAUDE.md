# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A learning-project REST API built with Python and FastAPI. Supports creating, viewing, filtering,
updating, and deleting tasks in a single shared **in-memory** list — data does not persist across
server restarts (ADR-001, see `docs/mini-adr.md`).

## Commands

Setup:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```
API at http://localhost:8000, interactive docs at http://localhost:8000/docs.

Run tests:
```bash
pytest
pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body  # single test
```
`pytest.ini` sets `pythonpath = .`, so tests import `app` directly — no package install needed.

Health check:
```bash
curl -X GET http://localhost:8000/health
```

## Architecture

- **`app/main.py`** — the only router. All `/tasks` endpoints (POST, GET list, GET by id, PATCH,
  DELETE) and `/health` are defined here directly on the `FastAPI()` instance; there is no
  `APIRouter` split despite `app/routers/` existing.
- **`app/storage.py`** — the actual data layer: a module-level `_tasks: dict[str, TaskResponse]`
  plus `add_task` / `get_all_tasks` / `get_task_by_id` / `update_task` / `delete_task` /
  `_reset()`. `get_all_tasks` applies all query filtering (status, priority, assignee, free-text
  `q` across title/description/assignee, `overdue`) in Python. This is the single source of truth
  for task data.
- **`app/store.py`** — a leftover/unused in-memory dict scaffold. Nothing imports it; don't
  confuse it with `app/storage.py`.
- **`app/models.py`** — all Pydantic schemas and enums (`TaskStatus`, `TaskPriority`,
  `TaskCreate`, `TaskUpdate`, `TaskResponse`). All models use `extra="forbid"`, so unknown fields
  in a request body are a 422, not silently ignored. Title is validated (non-blank, stripped,
  ≤200 chars) via `field_validator` on both `TaskCreate` and `TaskUpdate`.
- **`app/business_rules.py`** — status-transition rules for PATCH. `VALID_TRANSITIONS` is a
  frozenset of allowed `(from, to)` `TaskStatus` pairs; `validate_status_transition` raises 422
  (`HTTPException`) on a disallowed transition. Same-status "transitions" are always a no-op pass.
  Only `main.py`'s PATCH handler calls this — POST and other fields bypass it entirely.
- **`app/crud/`, `app/routers/`, `app/schemas/`, `app/services/`** — empty placeholder packages
  (each `__init__.py` is just a comment) reserved for a future layered refactor. All real logic
  currently lives in `main.py`, `storage.py`, `models.py`, and `business_rules.py`.
- **`app/frontend/index.html`** — a self-contained (no build step) Kanban-style UI that talks to
  the API directly from the browser. CORS in `main.py` is locked to
  `http://localhost:5500` / `http://127.0.0.1:5500` (e.g. VS Code Live Server) — update the
  `allow_origins` list if serving the frontend from elsewhere.

## Testing conventions

- `tests/conftest.py` provides a `client` fixture (`TestClient(app)`) and a `created_task` fixture
  (POSTs a default task). An autouse fixture calls `storage._reset()` before and after every test,
  so tests never leak task state between each other.
- `tests/test_tasks.py` is the pytest suite (endpoint-level, via `TestClient`).
- `tests/verify_a.py` is a standalone manual verification script (not pytest-based — run directly
  with `python tests/verify_a.py`) that checks `TaskCreate`/`TaskUpdate` validation behavior and
  prints PASS/FAIL lines.
