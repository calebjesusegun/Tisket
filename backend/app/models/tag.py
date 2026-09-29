from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.clock import utcnow
from app.db.base import Base
from app.db.types import UTCDateTime

TAG_NAME_MAX_LENGTH = 30


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(TAG_NAME_MAX_LENGTH), unique=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    def __repr__(self) -> str:
        return f"Tag(id={self.id!r}, name={self.name!r})"
