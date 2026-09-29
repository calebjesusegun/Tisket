from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies import PageParamsDep, SearchServiceDep
from app.schemas.common import Page
from app.schemas.search import SearchResult, SearchType

router = APIRouter(prefix="/search", tags=["search"])


@router.get(
    "",
    response_model=Page[SearchResult],
    summary="Search tasks and notes",
    description=(
        "Every word in `q` must match (prefix match on PostgreSQL). Results include "
        "`title_highlights` and `snippet` as segments; render segments with `match=true` "
        "highlighted."
    ),
)
def search(
    service: SearchServiceDep,
    page: PageParamsDep,
    q: Annotated[str, Query(min_length=1, max_length=200, pattern=r"\S", description="Query")],
    type: Annotated[SearchType, Query(description="Limit to tasks or notes")] = "all",
) -> Page[SearchResult]:
    return service.search(q, type, page)
