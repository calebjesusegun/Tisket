"""Migrations must build the same schema as the models, and be reversible."""

from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.manual_indexes import include_name
from app.repositories.search_repository import _SOURCES, SearchRepository
from tests.conftest import TEST_DATABASE_URL, downgrade_migrations, run_migrations

EXPECTED_TABLES = {"tasks", "notes", "tags", "task_tags", "note_tags", "alembic_version"}


def _diff(engine) -> list[object]:  # type: ignore[no-untyped-def]
    with engine.connect() as conn:
        ctx = MigrationContext.configure(
            conn, opts={"compare_type": True, "include_name": include_name}
        )
        return compare_metadata(ctx, Base.metadata)


def test_sqlite_migrations_upgrade_downgrade_and_match_models(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'migrate.db'}")
    run_migrations(engine)
    assert set(inspect(engine).get_table_names()) == EXPECTED_TABLES
    assert _diff(engine) == []

    downgrade_migrations(engine)
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}

    run_migrations(engine)
    assert set(inspect(engine).get_table_names()) == EXPECTED_TABLES
    engine.dispose()


@pytest.mark.skipif(not TEST_DATABASE_URL, reason="PostgreSQL only")
def test_postgres_schema_matches_models_and_has_fts_indexes(postgres_ready: None) -> None:
    assert TEST_DATABASE_URL is not None
    engine = create_engine(TEST_DATABASE_URL)
    assert _diff(engine) == []
    task_indexes = {ix["name"] for ix in inspect(engine).get_indexes("tasks")}
    note_indexes = {ix["name"] for ix in inspect(engine).get_indexes("notes")}
    assert "ix_tasks_fts" in task_indexes
    assert "ix_notes_fts" in note_indexes
    engine.dispose()


@pytest.mark.skipif(not TEST_DATABASE_URL, reason="PostgreSQL only")
def test_postgres_search_uses_fts_indexes(db: Session) -> None:
    """The search query's tsvector expression must match the GIN index expression exactly."""
    repo = SearchRepository(db)
    for source, index in (("task", "ix_tasks_fts"), ("note", "ix_notes_fts")):
        stmt = repo._matching(_SOURCES[source], ["groc"])
        compiled = stmt.compile(db.get_bind(), compile_kwargs={"literal_binds": True})
        db.execute(text("SET LOCAL enable_seqscan = off"))
        plan = "\n".join(r[0] for r in db.execute(text(f"EXPLAIN {compiled}")))
        assert index in plan, plan
    db.rollback()
