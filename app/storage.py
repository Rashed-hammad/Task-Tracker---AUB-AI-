from datetime import date, datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task in the in-memory store.

    Args:
        payload (TaskCreate): Validated task creation data.

    Returns:
        TaskResponse: The newly created task, with a generated UUID
            ``id`` and ``created_at``/``updated_at`` both set to the
            current UTC time.
    """
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
    """Return tasks from the in-memory store, optionally filtered.

    Filters are applied in sequence and combined with AND: ``status``
    (exact match), ``priority`` (exact match), ``assignee``
    (case-insensitive exact match; a blank/whitespace-only value is
    ignored), ``q`` (case-insensitive substring search across title,
    description, and assignee; a blank/whitespace-only value is
    ignored), and ``overdue`` (``True`` keeps tasks whose ``due_date``
    is set and before today; ``False`` keeps tasks whose ``due_date``
    is unset or not before today).

    Args:
        status (Optional[TaskStatus]): Exact-match status filter.
        priority (Optional[TaskPriority]): Exact-match priority filter.
        assignee (Optional[str]): Case-insensitive exact-match
            assignee filter.
        q (Optional[str]): Case-insensitive free-text search term.
        overdue (Optional[bool]): Overdue filter, see above.

    Returns:
        list[TaskResponse]: Tasks matching all supplied filters (all
            tasks if none are given).
    """
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
    """Look up a single task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        Optional[TaskResponse]: The matching task, or ``None`` if no
            task exists with the given id.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task.

    Only fields explicitly set on ``payload`` are applied
    (``model_dump(exclude_unset=True)``); if no fields were set, the
    task is returned unchanged. ``updated_at`` is refreshed to the
    current UTC time whenever at least one field is applied.

    Args:
        task_id (str): The task's unique id.
        payload (TaskUpdate): Fields to update.

    Returns:
        Optional[TaskResponse]: The updated task, or ``None`` if no
            task exists with the given id.
    """
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
    """Delete a task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        bool: ``True`` if a task was deleted, ``False`` if no task
            existed with the given id.
    """
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()
