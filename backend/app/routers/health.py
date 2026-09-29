import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import __version__
from app.dependencies import DbSession
from app.schemas.common import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse, "description": "Database unavailable"}},
)
def health(db: DbSession) -> HealthResponse | JSONResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Health check could not reach the database")
        body = HealthResponse(status="error", database="unavailable", version=__version__)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=body.model_dump()
        )
    return HealthResponse(status="ok", database="ok", version=__version__)
