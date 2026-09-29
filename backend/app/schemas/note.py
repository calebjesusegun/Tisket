from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.schemas.tag import TagRead
from app.schemas.task import TagNames, TaskSummary, Title

Content = Annotated[str, StringConstraints(max_length=20000)]


class NoteCreate(BaseModel):
    title: Title = Field(examples=["Meeting notes"])
    content: Content = Field("", description="Markdown text")
    pinned: bool = False
    task_id: int | None = Field(None, ge=1, description="Optional task this note belongs to")
    tags: TagNames = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: Title | None = None
    content: Content | None = None
    pinned: bool | None = None
    task_id: int | None = Field(None, ge=1, description="Set to null to unlink the task")
    tags: TagNames | None = None

    @field_validator("title", "content", "pinned", "tags")
    @classmethod
    def _not_null(cls, value: object) -> object:
        # Only `task_id` may be explicitly cleared with null.
        if value is None:
            raise ValueError("may not be null")
        return value


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    pinned: bool
    task_id: int | None
    task: TaskSummary | None
    tags: list[TagRead]
    created_at: datetime
    updated_at: datetime


class NoteFilters(BaseModel):
    tag: str | None = None
    pinned: bool | None = None
    task_id: int | None = None
