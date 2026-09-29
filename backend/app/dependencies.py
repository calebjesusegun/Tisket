"""FastAPI dependency providers. Tests override `get_db` / `get_clock` via dependency_overrides."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.clock import Clock, SystemClock
from app.core.config import Settings
from app.repositories.note_repository import NoteRepository
from app.repositories.search_repository import SearchRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.common import PageParams
from app.services.note_service import NoteService
from app.services.reminder_service import ReminderService
from app.services.search_service import SearchService
from app.services.tag_service import TagService
from app.services.task_service import TaskService


def get_settings_dep(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_db(request: Request) -> Iterator[Session]:
    session: Session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


def get_clock() -> Clock:
    return SystemClock()


def get_page_params(
    page: Annotated[int, Query(ge=1, description="Page number, starting at 1")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page (max 100)")] = 20,
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


DbSession = Annotated[Session, Depends(get_db)]
ClockDep = Annotated[Clock, Depends(get_clock)]
PageParamsDep = Annotated[PageParams, Depends(get_page_params)]


# --- Repositories and services -------------------------------------------------------------


def get_tag_service(db: DbSession) -> TagService:
    return TagService(db, TagRepository(db))


def get_task_service(
    db: DbSession, clock: ClockDep, tag_service: Annotated[TagService, Depends(get_tag_service)]
) -> TaskService:
    return TaskService(db, TaskRepository(db), tag_service, clock)


TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def get_note_service(db: DbSession, tag_service: TagServiceDep) -> NoteService:
    return NoteService(db, NoteRepository(db), TaskRepository(db), tag_service)


def get_search_service(db: DbSession, clock: ClockDep) -> SearchService:
    return SearchService(SearchRepository(db), clock)


def get_reminder_service(db: DbSession, clock: ClockDep) -> ReminderService:
    return ReminderService(db, TaskRepository(db), clock)


NoteServiceDep = Annotated[NoteService, Depends(get_note_service)]
SearchServiceDep = Annotated[SearchService, Depends(get_search_service)]
ReminderServiceDep = Annotated[ReminderService, Depends(get_reminder_service)]
