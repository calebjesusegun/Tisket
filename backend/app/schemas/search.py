from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.models.enums import TaskPriority, TaskStatus
from app.schemas.tag import TagRead

SearchType = Literal["all", "task", "note"]


class HighlightSegment(BaseModel):
    """A piece of text; `match` is true when it matched the query and should be highlighted."""

    text: str
    match: bool


class SearchResult(BaseModel):
    type: Literal["task", "note"]
    id: int
    title: str
    title_highlights: list[HighlightSegment]
    snippet: list[HighlightSegment]
    tags: list[TagRead]
    updated_at: datetime
    # Task-only fields
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_at: datetime | None = None
    # Note-only fields
    pinned: bool | None = None
