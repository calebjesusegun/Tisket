import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def make(**kwargs: str) -> Settings:
    return Settings(_env_file=None, **kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("postgres://u:p@h:5432/d", "postgresql+psycopg://u:p@h:5432/d"),
        ("postgresql://u@h/d", "postgresql+psycopg://u@h/d"),
        ("postgresql+psycopg://u@h/d", "postgresql+psycopg://u@h/d"),
        ("sqlite:///:memory:", "sqlite:///:memory:"),
    ],
)
def test_database_url_gets_psycopg_driver(given: str, expected: str) -> None:
    assert make(database_url=given).database_url == expected


def test_cors_origins_are_split_and_trimmed() -> None:
    settings = make(allowed_origins=" https://a.app/ , https://b.app ,")
    assert settings.cors_origins == ["https://a.app", "https://b.app"]


def test_production_rejects_wildcard_origins() -> None:
    with pytest.raises(ValidationError, match="ALLOWED_ORIGINS"):
        make(app_env="production", allowed_origins="*")


def test_production_rejects_empty_origins() -> None:
    with pytest.raises(ValidationError, match="ALLOWED_ORIGINS"):
        make(app_env="production", allowed_origins="")


def test_production_accepts_explicit_origin() -> None:
    settings = make(app_env="production", allowed_origins="https://tisket.vercel.app")
    assert settings.cors_origins == ["https://tisket.vercel.app"]


def test_get_settings_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "postgres://x@y/z")
    try:
        settings = get_settings()
        assert settings.app_env == "test"
        assert settings.database_url == "postgresql+psycopg://x@y/z"
    finally:
        get_settings.cache_clear()
