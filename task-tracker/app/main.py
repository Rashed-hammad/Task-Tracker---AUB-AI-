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
    """
    Returns the current service status and UTC timestamp.
    Use this endpoint to confirm the server is running before
    making any task-related requests.
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
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task





def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:

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
    print("Shutting down the server...")