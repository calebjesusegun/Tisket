"""App factory. `create_app()` builds a fully wired FastAPI app; tests call it per test."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.db.session import create_db_engine, create_session_factory
from app.routers import health
from app.schemas.common import ErrorResponse

API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=logging.INFO)

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Tasks, notes, tags, search and reminders for a shared Tisket workspace.",
        responses={422: {"model": ErrorResponse, "description": "Validation error"}},
    )

    engine = create_db_engine(settings)
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )
    register_error_handlers(app)

    app.include_router(health.router)
    return app


app = create_app()
