from fastapi import APIRouter, status

from app.dependencies import TagServiceDep
from app.schemas.common import ErrorResponse
from app.schemas.tag import TagCreate, TagRead, TagUpdate, TagWithCounts

router = APIRouter(prefix="/tags", tags=["tags"])

_ERRORS: dict[int | str, dict[str, object]] = {
    400: {"model": ErrorResponse, "description": "Invalid tag name"},
    404: {"model": ErrorResponse, "description": "Tag not found"},
    409: {"model": ErrorResponse, "description": "Tag name already exists"},
}


@router.get("", response_model=list[TagWithCounts], summary="List tags with usage counts")
def list_tags(service: TagServiceDep) -> list[TagWithCounts]:
    return [TagWithCounts(**row) for row in service.list_tags()]


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED, responses=_ERRORS)
def create_tag(data: TagCreate, service: TagServiceDep) -> TagRead:
    return TagRead.model_validate(service.create(data.name))


@router.patch("/{tag_id}", response_model=TagRead, responses=_ERRORS, summary="Rename a tag")
def rename_tag(tag_id: int, data: TagUpdate, service: TagServiceDep) -> TagRead:
    return TagRead.model_validate(service.rename(tag_id, data.name))


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, responses=_ERRORS)
def delete_tag(tag_id: int, service: TagServiceDep) -> None:
    service.delete(tag_id)
