from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.business_rules import validate_status_transition

import os
from dotenv import load_dotenv

from app import storage
from app.models import TaskCreate, TaskResponse
from app.models import (

    TaskCreate,

    TaskUpdate,

    TaskResponse,

    TaskStatus,

    TaskPriority,

)
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 — In-memory Task Tracker REST API built with FastAPI.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    summary="Health check",
    tags=["Health"],
    response_description="Service is running",
)
def health_check() -> JSONResponse:
    """Report basic service liveness.

    Returns the current UTC timestamp and a static "ok" status so
    callers can confirm the API process is up before making any
    task-related requests.

    Returns:
        JSONResponse: HTTP 200 with body
            ``{"status": "ok", "timestamp": <ISO 8601 UTC timestamp>}``.

    Example:
        GET /health -> 200
        {"status": "ok", "timestamp": "2026-07-18T14:07:07.886794+00:00"}
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.post(
    "/tasks",
    tags=["tasks"],
    status_code=201,
    response_model=TaskResponse,
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Args:
        payload (TaskCreate): Task fields to create. ``title`` is
            required (non-blank after stripping, at most 200 characters).
            ``status`` defaults to ``TaskStatus.TODO`` and ``priority``
            defaults to ``TaskPriority.MEDIUM`` when omitted. Unknown
            fields are rejected (``extra="forbid"``).

    Returns:
        TaskResponse: The newly created task, including a generated
            ``id`` and ``created_at``/``updated_at`` timestamps.

    Raises:
        [VERIFY] No HTTPException is raised in this function body.
        Invalid payloads (missing/blank title, unknown fields, wrong
        types) are rejected by FastAPI/Pydantic request validation
        with an automatic HTTP 422 before this function is called.

    Example:
        POST /tasks {"title": "Write docs"} -> 201 TaskResponse
    """
    return storage.add_task(payload)

@app.get(

    "/tasks",

    tags=["tasks"],

    response_model=list[TaskResponse],

)

def list_tasks(

    status: TaskStatus | None = None,

    priority: TaskPriority | None = None,

    assignee: str | None = None,

    q: str | None = None,

    overdue: bool | None = None,

) -> list[TaskResponse]:
    """List tasks, optionally filtered.

    All supplied filters are combined with AND; omitted filters
    (``None``) are not applied. Filtering itself is performed by
    ``storage.get_all_tasks``.

    Args:
        status (TaskStatus | None): Exact-match filter on task status.
        priority (TaskPriority | None): Exact-match filter on task
            priority.
        assignee (str | None): Case-insensitive exact-match filter on
            assignee. A blank/whitespace-only value is treated as
            "no filter".
        q (str | None): Case-insensitive free-text search across
            title, description, and assignee. A blank/whitespace-only
            value is treated as "no filter".
        overdue (bool | None): When ``True``, only tasks with a
            ``due_date`` in the past are returned. When ``False``,
            only tasks whose ``due_date`` is unset or not in the past
            are returned. When ``None``, no overdue filtering is
            applied.

    Returns:
        list[TaskResponse]: Tasks matching all supplied filters (all
            tasks if none are given).

    Example:
        GET /tasks?status=ToDo&priority=High&overdue=true
    """

    return storage.get_all_tasks(
        status=status,
        priority=priority,
        assignee=assignee,
        q=q,
        overdue=overdue,
    )

@app.get(
    "/tasks/{task_id}",
    tags=["tasks"],
    response_model=TaskResponse,
)
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task exists with the given id.

    Example:
        GET /tasks/{task_id} -> 200 TaskResponse
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task




def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """[VERIFY] Unreachable duplicate — not registered as a route.

    This definition has no ``@app.patch``/``@app.put``/etc. decorator
    above it, so FastAPI never registers it as a route handler. It is
    immediately shadowed by the identically-named, decorated
    ``update_task`` (the ``@app.patch("/tasks/{task_id}")`` handler
    further down in this file), so this function is dead code and is
    never called at runtime. Flagging rather than removing, since
    deleting it would be a logic/structure change outside this task's
    scope — recommend confirming and removing it separately.
    """

    task = storage.update_task(task_id, payload)

    if task is None:

        raise HTTPException(

            status_code=404,

            detail=f"Task with id {task_id} not found",

        )

    return task



@app.delete(

    "/tasks/{task_id}",

    tags=["tasks"],

    status_code=status.HTTP_204_NO_CONTENT,

)

def delete_task(task_id: str):
    """Delete a task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        None: No content is returned on success.

    Raises:
        HTTPException: 404 if no task exists with the given id.

    Example:
        DELETE /tasks/{task_id} -> 204
    """

    deleted = storage.delete_task(task_id)

    if not deleted:

        raise HTTPException(

            status_code=404,

            detail=f"Task with id {task_id} not found",

        )

    return None


    # PATCH ROUTE ONLY FROM app/main.py
@app.patch(
    "/tasks/{task_id}",
    tags=["tasks"],
    response_model=TaskResponse,
)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task.

    Only fields explicitly present in the request body are applied
    (``exclude_unset=True``); omitted fields are left unchanged. If
    ``status`` is included and differs from the task's current status,
    the transition is validated against the allowed state machine
    (``app.business_rules.VALID_TRANSITIONS``) before the update is
    applied. Setting ``status`` to its current value is always a
    no-op pass (see ``validate_status_transition``).

    Args:
        task_id (str): The task's unique id.
        payload (TaskUpdate): Fields to update. Unknown fields are
            rejected (``extra="forbid"``).

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if no task exists with the given id.
        HTTPException: 422 if ``status`` is set to a value that is not
            a valid transition from the task's current status.

    Example:
        PATCH /tasks/{task_id} {"status": "InProgress"} -> 200 TaskResponse
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with id {task_id} not found",
            )

        validate_status_transition(existing.status, payload.status)

    task = storage.update_task(task_id, payload)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )

    return task


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Log a message when the application is shutting down.

    [VERIFY] Registered via the deprecated ``@app.on_event("shutdown")``
    API (FastAPI/Starlette emit a DeprecationWarning recommending
    lifespan event handlers instead). Left as-is since changing it
    would alter runtime wiring, which is outside this task's scope.

    Returns:
        None
    """
    print("Shutting down the server...")
