"""Indexes created by hand in migrations (PostgreSQL full-text GIN indexes).

The models cannot declare these portably, so Alembic autogenerate is told to ignore them.
"""

MANUAL_INDEXES = frozenset({"ix_tasks_fts", "ix_notes_fts"})


def include_name(name: str | None, type_: str, _parent_names: object) -> bool:
    return not (type_ == "index" and name in MANUAL_INDEXES)
