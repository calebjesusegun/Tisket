from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies import ClockDep, PageParamsDep, ReminderServiceDep
from app.schemas.common import ErrorResponse, Page
from app.schemas.reminder import DismissAllResponse
from app.schemas.task import TaskRead
from app.services.reminder_rules import DUE_SOON_HOURS
from app.services.task_service import task_to_read

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get(
    "/due-soon", response_model=Page[TaskRead], summary="Open tasks due in the next N hours"
)
def due_soon(
    service: ReminderServiceDep,
    page: PageParamsDep,
    hours: Annotated[int, Query(ge=1, le=168, description="Window size in hours")] = DUE_SOON_HOURS,
) -> Page[TaskRead]:
    return service.due_soon(page, hours)


@router.get("/overdue", response_model=Page[TaskRead], summary="Open tasks past their due time")
def overdue(service: ReminderServiceDep, page: PageParamsDep) -> Page[TaskRead]:
    return service.overdue(page)


@router.get(
    "/notifications",
    response_model=Page[TaskRead],
    summary="In-app notifications: due tasks not yet dismissed",
)
def notifications(service: ReminderServiceDep, page: PageParamsDep) -> Page[TaskRead]:
    return service.notifications(page)


@router.post(
    "/{task_id}/dismiss",
    response_model=TaskRead,
    responses={404: {"model": ErrorResponse, "description": "Task not found"}},
    summary="Dismiss the notification for a task",
)
def dismiss(task_id: int, service: ReminderServiceDep, clock: ClockDep) -> TaskRead:
    return task_to_read(service.dismiss(task_id), clock.now())


@router.post("/dismiss-all", response_model=DismissAllResponse, summary="Dismiss all notifications")
def dismiss_all(service: ReminderServiceDep) -> DismissAllResponse:
    return DismissAllResponse(dismissed=service.dismiss_all())
