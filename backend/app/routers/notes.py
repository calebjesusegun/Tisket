from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import NoteServiceDep, PageParamsDep
from app.schemas.common import ErrorResponse, Page
from app.schemas.note import NoteCreate, NoteFilters, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])

_NOT_FOUND: dict[int | str, dict[str, object]] = {
    404: {"model": ErrorResponse, "description": "Note not found"}
}
_BAD_REQUEST: dict[int | str, dict[str, object]] = {
    400: {"model": ErrorResponse, "description": "Invalid tag or unknown task_id"}
}


@router.get("", response_model=Page[NoteRead], summary="List notes (pinned first)")
def list_notes(
    service: NoteServiceDep,
    page: PageParamsDep,
    tag: Annotated[str | None, Query(max_length=60)] = None,
    pinned: bool | None = None,
    task_id: Annotated[int | None, Query(ge=1)] = None,
) -> Page[NoteRead]:
    return service.list_notes(NoteFilters(tag=tag, pinned=pinned, task_id=task_id), page)


@router.post(
    "", response_model=NoteRead, status_code=status.HTTP_201_CREATED, responses=_BAD_REQUEST
)
def create_note(data: NoteCreate, service: NoteServiceDep) -> NoteRead:
    return NoteRead.model_validate(service.create(data))


@router.get("/{note_id}", response_model=NoteRead, responses=_NOT_FOUND)
def get_note(note_id: int, service: NoteServiceDep) -> NoteRead:
    return NoteRead.model_validate(service.get(note_id))


@router.patch("/{note_id}", response_model=NoteRead, responses={**_NOT_FOUND, **_BAD_REQUEST})
def update_note(note_id: int, data: NoteUpdate, service: NoteServiceDep) -> NoteRead:
    return NoteRead.model_validate(service.update(note_id, data))


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
def delete_note(note_id: int, service: NoteServiceDep) -> None:
    service.delete(note_id)
