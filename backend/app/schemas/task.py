from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

from app.models.enums import TaskPriority, TaskStatus
from app.schemas.tag import TagRead

MAX_TAGS = 10

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Description = Annotated[str, StringConstraints(max_length=5000)]


def _as_utc(value: datetime | None) -> datetime | None:
    """Naive datetimes are interpreted as UTC; aware ones are converted to UTC."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


DueAt = Annotated[datetime | None, AfterValidator(_as_utc)]
TagNames = Annotated[list[str], Field(max_length=MAX_TAGS)]


class TaskCreate(BaseModel):
    title: Title = Field(examples=["Buy groceries"])
    description: Description = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_at: DueAt = None
    tags: TagNames = Field(default_factory=list, examples=[["home", "errands"]])


class TaskUpdate(BaseModel):
    title: Title | None = None
    description: Description | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_at: DueAt = None
    tags: TagNames | None = None

    @field_validator("title", "description", "status", "priority", "tags")
    @classmethod
    def _not_null(cls, value: object) -> object:
        # Only `due_at` may be explicitly cleared with null.
        if value is None:
            raise ValueError("may not be null")
        return value


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead]
    is_overdue: bool = False
    is_due_soon: bool = False


class TaskSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TaskStatus


TaskSortField = Literal["due_at", "priority", "created_at", "updated_at", "title"]
SortOrder = Literal["asc", "desc"]


class TaskFilters(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    tag: str | None = None
    sort: TaskSortField = "created_at"
    order: SortOrder = "desc"
