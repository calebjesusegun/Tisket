from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import PageParamsDep, TaskServiceDep
from app.models import TaskPriority, TaskStatus
from app.schemas.common import ErrorResponse, Page
from app.schemas.task import SortOrder, TaskCreate, TaskFilters, TaskRead, TaskSortField, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])

_NOT_FOUND: dict[int | str, dict[str, object]] = {
    404: {"model": ErrorResponse, "description": "Task not found"}
}
_BAD_TAG: dict[int | str, dict[str, object]] = {
    400: {"model": ErrorResponse, "description": "Invalid tag name"}
}


@router.get("", response_model=Page[TaskRead], summary="List tasks with filters and sorting")
def list_tasks(
    service: TaskServiceDep,
    page: PageParamsDep,
    status_: Annotated[
        list[TaskStatus] | None,
        Query(alias="status", description="Filter by status; repeat for several"),
    ] = None,
    priority: TaskPriority | None = None,
    tag: Annotated[str | None, Query(max_length=60, description="Tag name")] = None,
    sort: TaskSortField = "created_at",
    order: SortOrder = "desc",
) -> Page[TaskRead]:
    filters = TaskFilters(priority=priority, tag=tag, sort=sort, order=order)
    return service.list_tasks(filters, page, statuses=status_)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED, responses=_BAD_TAG)
def create_task(data: TaskCreate, service: TaskServiceDep) -> TaskRead:
    return service.to_read(service.create(data))


@router.get("/{task_id}", response_model=TaskRead, responses=_NOT_FOUND)
def get_task(task_id: int, service: TaskServiceDep) -> TaskRead:
    return service.to_read(service.get(task_id))


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    responses={**_NOT_FOUND, **_BAD_TAG},
    summary="Update a task (partial). Set status to 'done' to complete it.",
)
def update_task(task_id: int, data: TaskUpdate, service: TaskServiceDep) -> TaskRead:
    return service.to_read(service.update(task_id, data))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, responses=_NOT_FOUND)
def delete_task(task_id: int, service: TaskServiceDep) -> None:
    service.delete(task_id)
