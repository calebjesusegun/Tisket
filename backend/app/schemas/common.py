import math
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def build(cls, items: list[T], total: int, page: int, page_size: int) -> "Page[T]":
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total else 0,
        )


class PageParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    """Documented shape of every error response."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {"code": "not_found", "message": "Task 42 not found", "details": None}
            }
        }
    )

    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str
    database: str
    version: str
