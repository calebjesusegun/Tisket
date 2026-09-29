"""Full-text search queries.

PostgreSQL uses `to_tsvector`/`to_tsquery` with prefix matching and `ts_headline` for highlights.
The tsvector expressions are emitted verbatim so they match the GIN indexes in the migration.
SQLite (tests only) falls back to case-insensitive LIKE: every term must appear in the title
or the body.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import (
    ColumnElement,
    Float,
    Select,
    and_,
    case,
    cast,
    func,
    literal,
    literal_column,
    or_,
    select,
    union_all,
)
from sqlalchemy.orm import Session

from app.models import Note, Task

# Private-use characters that never appear in normal text; parsed into segments by the service.
START_SEL = ""
STOP_SEL = ""
_TITLE_OPTS = f"StartSel={START_SEL}, StopSel={STOP_SEL}, HighlightAll=true"
_BODY_OPTS = (
    f"StartSel={START_SEL}, StopSel={STOP_SEL}, MaxWords=30, MinWords=12, "
    'MaxFragments=2, FragmentDelimiter=" … "'
)

# Must stay identical to the index expressions in the initial migration. Title = A, body = B.
TASKS_TSV: ColumnElement[Any] = literal_column(
    "(setweight(to_tsvector('english'::regconfig, coalesce(tasks.title, '')), 'A') || "
    "setweight(to_tsvector('english'::regconfig, coalesce(tasks.description, '')), 'B'))"
)
NOTES_TSV: ColumnElement[Any] = literal_column(
    "(setweight(to_tsvector('english'::regconfig, coalesce(notes.title, '')), 'A') || "
    "setweight(to_tsvector('english'::regconfig, coalesce(notes.content, '')), 'B'))"
)
ENGLISH: ColumnElement[Any] = literal_column("'english'::regconfig")


@dataclass(frozen=True)
class SearchHit:
    type: str
    id: int
    title_headline: str | None = None
    body_headline: str | None = None


@dataclass(frozen=True)
class _Source:
    type: str
    model: Any
    body: Any
    tsv: ColumnElement[Any]


_SOURCES = {
    "task": _Source("task", Task, Task.description, TASKS_TSV),
    "note": _Source("note", Note, Note.content, NOTES_TSV),
}


def _like(term: str) -> str:
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def to_prefix_tsquery(terms: list[str]) -> str:
    """['groc', 'list'] -> "groc:* & list:*" (terms are already reduced to word characters)."""
    return " & ".join(f"{term}:*" for term in terms)


class SearchRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.is_postgres = session.get_bind().dialect.name == "postgresql"

    def search(
        self, terms: list[str], types: list[str], offset: int, limit: int
    ) -> tuple[list[SearchHit], int]:
        selects = [self._matching(_SOURCES[t], terms) for t in types]
        combined = union_all(*selects).subquery() if len(selects) > 1 else selects[0].subquery()
        total = self.session.scalar(select(func.count()).select_from(combined)) or 0
        rows = self.session.execute(
            select(combined.c.type, combined.c.id)
            .order_by(combined.c.rank.desc(), combined.c.updated_at.desc(), combined.c.id.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        hits = [SearchHit(type=row.type, id=row.id) for row in rows]
        if self.is_postgres and hits:
            hits = self._with_headlines(hits, terms)
        return hits, total

    def load_tasks(self, ids: list[int]) -> dict[int, Task]:
        if not ids:
            return {}
        return {t.id: t for t in self.session.scalars(select(Task).where(Task.id.in_(ids)))}

    def load_notes(self, ids: list[int]) -> dict[int, Note]:
        if not ids:
            return {}
        return {n.id: n for n in self.session.scalars(select(Note).where(Note.id.in_(ids)))}

    # --- internals ------------------------------------------------------------------------

    def _query(self, terms: list[str]) -> ColumnElement[Any]:
        return func.to_tsquery(ENGLISH, to_prefix_tsquery(terms))

    def _matching(self, source: _Source, terms: list[str]) -> Select[Any]:
        model = source.model
        updated_at: ColumnElement[datetime] = model.updated_at
        if self.is_postgres:
            query = self._query(terms)
            where: ColumnElement[bool] = source.tsv.op("@@")(query)
            rank: ColumnElement[Any] = func.ts_rank(source.tsv, query)
        else:
            where = and_(
                *(
                    or_(
                        model.title.ilike(_like(t), escape="\\"),
                        source.body.ilike(_like(t), escape="\\"),
                    )
                    for t in terms
                )
            )
            # Title matches rank above body-only matches.
            rank = cast(
                case(
                    (and_(*(model.title.ilike(_like(t), escape="\\") for t in terms)), 1.0),
                    else_=0.0,
                ),
                Float,
            )
        return select(
            literal(source.type).label("type"),
            model.id.label("id"),
            rank.label("rank"),
            updated_at.label("updated_at"),
        ).where(where)

    def _with_headlines(self, hits: list[SearchHit], terms: list[str]) -> list[SearchHit]:
        query = self._query(terms)
        headlines: dict[tuple[str, int], tuple[str, str]] = {}
        for type_, source in _SOURCES.items():
            ids = [h.id for h in hits if h.type == type_]
            if not ids:
                continue
            model = source.model
            rows = self.session.execute(
                select(
                    model.id,
                    func.ts_headline(ENGLISH, model.title, query, _TITLE_OPTS),
                    func.ts_headline(ENGLISH, source.body, query, _BODY_OPTS),
                ).where(model.id.in_(ids))
            ).all()
            for row_id, title_hl, body_hl in rows:
                headlines[(type_, row_id)] = (title_hl, body_hl)
        return [SearchHit(h.type, h.id, *headlines.get((h.type, h.id), (None, None))) for h in hits]
