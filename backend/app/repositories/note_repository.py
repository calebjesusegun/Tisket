from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Note, Tag
from app.schemas.common import PageParams
from app.schemas.note import NoteFilters


class NoteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, note_id: int) -> Note | None:
        return self.session.get(Note, note_id)

    def add(self, note: Note) -> Note:
        self.session.add(note)
        self.session.flush()
        return note

    def delete(self, note: Note) -> None:
        self.session.delete(note)
        self.session.flush()

    def find(self, filters: NoteFilters, page: PageParams) -> tuple[list[Note], int]:
        stmt = self._filtered(filters)
        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = (
            stmt.order_by(Note.pinned.desc(), Note.updated_at.desc(), Note.id.desc())
            .offset(page.offset)
            .limit(page.page_size)
        )
        return list(self.session.scalars(stmt)), total

    @staticmethod
    def _filtered(filters: NoteFilters) -> Select[tuple[Note]]:
        stmt = select(Note)
        if filters.tag:
            stmt = stmt.where(Note.tags.any(Tag.name == filters.tag))
        if filters.pinned is not None:
            stmt = stmt.where(Note.pinned.is_(filters.pinned))
        if filters.task_id is not None:
            stmt = stmt.where(Note.task_id == filters.task_id)
        return stmt
