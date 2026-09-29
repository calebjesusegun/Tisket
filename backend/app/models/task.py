from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.db.base import Base
from app.db.types import UTCDateTime
from app.models.associations import task_tags
from app.models.enums import TaskPriority, TaskStatus
from app.models.tag import Tag

if TYPE_CHECKING:
    from app.models.note import Note

TITLE_MAX_LENGTH = 200


def _enum_values(enum_cls: type[TaskStatus] | type[TaskPriority]) -> list[str]:
    return [member.value for member in enum_cls]


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            name="task_status",
            native_enum=False,
            length=20,
            values_callable=_enum_values,
            create_constraint=True,
            validate_strings=True,
        ),
        default=TaskStatus.TODO,
        index=True,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(
            TaskPriority,
            name="task_priority",
            native_enum=False,
            length=20,
            values_callable=_enum_values,
            create_constraint=True,
            validate_strings=True,
        ),
        default=TaskPriority.MEDIUM,
        index=True,
    )
    due_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), index=True)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    reminder_dismissed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    tags: Mapped[list[Tag]] = relationship(secondary=task_tags, lazy="selectin", order_by=Tag.name)
    notes: Mapped[list["Note"]] = relationship(back_populates="task", passive_deletes=True)

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, title={self.title!r}, status={self.status!r})"
