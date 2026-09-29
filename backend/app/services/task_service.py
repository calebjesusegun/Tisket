"""Task rules: completion timestamps, reminder reset on new due dates, tags on the fly."""

from sqlalchemy.orm import Session

from app.core.clock import Clock
from app.core.errors import NotFoundError
from app.models import Tag, Task, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.common import Page, PageParams
from app.schemas.task import TaskCreate, TaskFilters, TaskRead, TaskUpdate
from app.services import reminder_rules
from app.services.tag_service import TagService, normalize_tag_name


class TaskService:
    def __init__(
        self,
        session: Session,
        repository: TaskRepository,
        tag_service: TagService,
        clock: Clock,
    ) -> None:
        self.session = session
        self.repository = repository
        self.tag_service = tag_service
        self.clock = clock

    def to_read(self, task: Task) -> TaskRead:
        now = self.clock.now()
        read = TaskRead.model_validate(task)
        read.is_overdue = reminder_rules.is_overdue(task, now)
        read.is_due_soon = reminder_rules.is_due_soon(task, now)
        return read

    def get(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise NotFoundError(f"Task {task_id} not found")
        return task

    def list_tasks(
        self, filters: TaskFilters, page: PageParams, statuses: list[TaskStatus] | None = None
    ) -> Page[TaskRead]:
        if filters.tag:
            filters = filters.model_copy(update={"tag": normalize_tag_name(filters.tag)})
        items, total = self.repository.find(
            filters, page, [s.value for s in statuses] if statuses else None
        )
        return Page.build([self.to_read(t) for t in items], total, page.page, page.page_size)

    def create(self, data: TaskCreate) -> Task:
        task = Task(
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            due_at=data.due_at,
            tags=self._tags(data.tags),
        )
        self._apply_completion(task, previous=None)
        self.repository.add(task)
        self.session.commit()
        return task

    def update(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get(task_id)
        changes = data.model_dump(exclude_unset=True)
        previous_status = task.status
        if "tags" in changes:
            task.tags = self._tags(changes.pop("tags"))
        if "due_at" in changes and changes["due_at"] != task.due_at:
            # A new due date is a new reminder: forget any earlier dismissal.
            task.reminder_dismissed_at = None
        for field, value in changes.items():
            setattr(task, field, value)
        self._apply_completion(task, previous=previous_status)
        self.session.commit()
        return task

    def delete(self, task_id: int) -> None:
        self.repository.delete(self.get(task_id))
        self.session.commit()

    def _tags(self, names: list[str]) -> list[Tag]:
        # Same order as when tags are loaded from the database.
        return sorted(self.tag_service.resolve(names), key=lambda tag: tag.name)

    def _apply_completion(self, task: Task, previous: TaskStatus | None) -> None:
        if task.status == TaskStatus.DONE and previous != TaskStatus.DONE:
            task.completed_at = self.clock.now()
        elif task.status != TaskStatus.DONE:
            task.completed_at = None
