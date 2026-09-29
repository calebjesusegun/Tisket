from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.db.base import Base
from app.db.types import UTCDateTime
from app.models.associations import note_tags
from app.models.tag import Tag
from app.models.task import Task

TITLE_MAX_LENGTH = 200


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    content: Mapped[str] = mapped_column(Text, default="")
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    tags: Mapped[list[Tag]] = relationship(secondary=note_tags, lazy="selectin", order_by=Tag.name)
    task: Mapped[Task | None] = relationship(back_populates="notes", lazy="selectin")

    def __repr__(self) -> str:
        return f"Note(id={self.id!r}, title={self.title!r})"
