from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and normalize a task title.

        Args:
            v (str): The raw title value.

        Returns:
            str: The stripped title.

        Raises:
            ValueError: If the stripped title is empty, or longer than
                200 characters. Pydantic surfaces this as part of an
                HTTP 422 response when the model is used as a FastAPI
                request body.
        """
        stripped = v.strip()
        if not stripped:
            raise ValueError("title cannot be blank")
        if len(stripped) > 200:
            raise ValueError("title must be at most 200 characters")
        return stripped


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize an optional task title.

        Args:
            v (Optional[str]): The raw title value, or ``None`` if the
                field is not being updated.

        Returns:
            Optional[str]: ``None`` if ``v`` is ``None``, otherwise the
                stripped title.

        Raises:
            ValueError: If ``v`` is not ``None`` and the stripped
                title is empty, or longer than 200 characters.
        """
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("title cannot be blank")
        if len(stripped) > 200:
            raise ValueError("title must be at most 200 characters")
        return stripped


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
