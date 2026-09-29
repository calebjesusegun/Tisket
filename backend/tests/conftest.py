"""Shared fixtures.

By default each test gets a fresh app and a fresh in-memory SQLite database.
Set TEST_DATABASE_URL to a PostgreSQL URL to run the whole suite against PostgreSQL: the schema
is rebuilt with Alembic once per session and tables are truncated between tests.
"""

import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.base import Base
from app.dependencies import get_clock
from app.main import create_app

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
BACKEND_DIR = Path(__file__).resolve().parent.parent
FIXED_NOW = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)


class FixedClock:
    """A controllable clock for deterministic reminder tests."""

    def __init__(self, now: datetime = FIXED_NOW) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, **kwargs: float) -> None:
        self._now += timedelta(**kwargs)

    def set(self, now: datetime) -> None:
        self._now = now


def alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.attributes["configure_logger"] = False
    return cfg


def run_migrations(engine: Engine, revision: str = "head") -> None:
    with engine.begin() as connection:
        cfg = alembic_config()
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, revision)


def downgrade_migrations(engine: Engine, revision: str = "base") -> None:
    with engine.begin() as connection:
        cfg = alembic_config()
        cfg.attributes["connection"] = connection
        command.downgrade(cfg, revision)


@pytest.fixture(scope="session")
def postgres_ready() -> Iterator[None]:
    """Rebuild the PostgreSQL test schema from scratch with Alembic, once per session."""
    if not TEST_DATABASE_URL:
        yield
        return
    url = Settings(_env_file=None, database_url=TEST_DATABASE_URL).database_url  # type: ignore[call-arg]
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    run_migrations(engine)
    engine.dispose()
    yield


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture
def settings() -> Settings:
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        app_env="test",
        database_url=TEST_DATABASE_URL or "sqlite+pysqlite:///:memory:",
        allowed_origins="https://tisket.example.com",
    )


@pytest.fixture
def app(settings: Settings, clock: FixedClock, postgres_ready: None) -> Iterator[FastAPI]:
    application = create_app(settings)
    engine: Engine = application.state.engine
    if settings.is_sqlite:
        Base.metadata.create_all(engine)
    else:
        tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
    application.dependency_overrides[get_clock] = lambda: clock
    yield application
    engine.dispose()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db(app: FastAPI) -> Iterator[Session]:
    session: Session = app.state.session_factory()
    try:
        yield session
    finally:
        session.close()
