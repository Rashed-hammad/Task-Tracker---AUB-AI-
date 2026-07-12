from datetime import date, datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee: Optional[str] = None,
    q: Optional[str] = None,
    overdue: Optional[bool] = None,
) -> list[TaskResponse]:
    tasks = list(_tasks.values())

    if status is not None:
        tasks = [t for t in tasks if t.status == status]

    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority]

    if assignee is not None:
        assignee_filter = assignee.strip().lower()
        if assignee_filter:
            tasks = [
                t for t in tasks if (t.assignee or "").lower() == assignee_filter
            ]

    if q is not None:
        search_term = q.strip().lower()
        if search_term:
            tasks = [
                t
                for t in tasks
                if search_term in " ".join(
                    [
                        t.title.lower(),
                        t.description.lower(),
                        (t.assignee or "").lower(),
                    ]
                )
            ]

    if overdue is not None:
        today = date.today()
        tasks = [
            t
            for t in tasks
            if (t.due_date is not None and t.due_date < today) is overdue
        ]

    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return task

    updated = task.model_copy(
        update={**updates, "updated_at": datetime.now(timezone.utc)}
    )
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()
