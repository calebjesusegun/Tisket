from collections.abc import Iterable
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Tag, note_tags, task_tags


class TagRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, tag_id: int) -> Tag | None:
        return self.session.get(Tag, tag_id)

    def get_by_name(self, name: str) -> Tag | None:
        return self.session.scalar(select(Tag).where(Tag.name == name))

    def get_by_names(self, names: Iterable[str]) -> list[Tag]:
        names = list(names)
        if not names:
            return []
        return list(self.session.scalars(select(Tag).where(Tag.name.in_(names))))

    def add(self, tag: Tag) -> Tag:
        self.session.add(tag)
        self.session.flush()
        return tag

    def delete(self, tag: Tag) -> None:
        self.session.delete(tag)
        self.session.flush()

    def list_with_counts(self) -> list[dict[str, Any]]:
        task_counts = (
            select(task_tags.c.tag_id, func.count().label("n"))
            .group_by(task_tags.c.tag_id)
            .subquery()
        )
        note_counts = (
            select(note_tags.c.tag_id, func.count().label("n"))
            .group_by(note_tags.c.tag_id)
            .subquery()
        )
        stmt = (
            select(
                Tag.id,
                Tag.name,
                func.coalesce(task_counts.c.n, 0).label("task_count"),
                func.coalesce(note_counts.c.n, 0).label("note_count"),
            )
            .outerjoin(task_counts, task_counts.c.tag_id == Tag.id)
            .outerjoin(note_counts, note_counts.c.tag_id == Tag.id)
            .order_by(Tag.name)
        )
        return [dict(row._mapping) for row in self.session.execute(stmt)]
