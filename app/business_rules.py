# FILE: app/business_rules.py

from fastapi import HTTPException, status

from app.models import TaskStatus


VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.TODO),

})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate a task status transition, raising if it's not allowed.

    Same-status "transitions" (``current == new``) are always treated
    as a no-op and pass without error. Otherwise the ``(current, new)``
    pair must be a member of ``VALID_TRANSITIONS``.

    Args:
        current (TaskStatus): The task's existing status.
        new (TaskStatus): The requested new status.

    Returns:
        None

    Raises:
        HTTPException: 422 if ``(current, new)`` is not in
            ``VALID_TRANSITIONS``, with a ``detail`` message listing
            all allowed transitions.
    """
    if current == new:
        return

    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted(
            {f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS}
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Invalid status transition from {current.value} "
                f"to {new.value}. Allowed transitions: {allowed}"
            ),
        )
