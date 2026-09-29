"""Application settings loaded from environment variables (and an optional .env file)."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_POSTGRES_PREFIXES = ("postgres://", "postgresql://")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Tisket API"
    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://postgres@localhost:5432/tisket"
    allowed_origins: str = "http://localhost:5173"

    @field_validator("database_url")
    @classmethod
    def _use_psycopg_driver(cls, value: str) -> str:
        """Hosting providers hand out `postgres://` URLs; SQLAlchemy needs an explicit driver."""
        for prefix in _POSTGRES_PREFIXES:
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value.removeprefix(prefix)
        return value

    @model_validator(mode="after")
    def _strict_cors_in_production(self) -> "Settings":
        if self.app_env == "production" and (not self.cors_origins or "*" in self.cors_origins):
            raise ValueError("ALLOWED_ORIGINS must list explicit origins in production")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
