"""SQLAlchemy models. Importing this package registers every table on `Base.metadata`."""

from app.models.associations import note_tags, task_tags
from app.models.enums import TaskPriority, TaskStatus
from app.models.note import Note
from app.models.tag import Tag
from app.models.task import Task

__all__ = ["Note", "Tag", "Task", "TaskPriority", "TaskStatus", "note_tags", "task_tags"]
