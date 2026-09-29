from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings


def create_db_engine(settings: Settings) -> Engine:
    url = settings.database_url
    if not settings.is_sqlite:
        return create_engine(url, pool_pre_ping=True)

    kwargs: dict[str, object] = {"connect_args": {"check_same_thread": False}}
    if ":memory:" in url or url.rstrip("/") in ("sqlite:", "sqlite+pysqlite:"):
        # One shared connection so every session sees the same in-memory database.
        kwargs["poolclass"] = StaticPool
    engine = create_engine(url, **kwargs)

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _record):  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
