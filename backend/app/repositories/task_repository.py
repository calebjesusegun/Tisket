from datetime import datetime

from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.orm import Session

from app.models import Tag, Task, TaskPriority, TaskStatus
from app.models.enums import PRIORITY_RANK
from app.schemas.common import PageParams
from app.schemas.task import TaskFilters

_PRIORITY_ORDER = case(
    *((Task.priority == priority, rank) for priority, rank in PRIORITY_RANK.items()),
    else_=0,
)


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, task_id: int) -> Task | None:
        return self.session.get(Task, task_id)

    def add(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        return task

    def delete(self, task: Task) -> None:
        self.session.delete(task)
        self.session.flush()

    def find(
        self,
        filters: TaskFilters,
        page: PageParams,
        statuses: list[str] | None = None,
    ) -> tuple[list[Task], int]:
        stmt = self._filtered(filters, statuses)
        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = self._ordered(stmt, filters).offset(page.offset).limit(page.page_size)
        return list(self.session.scalars(stmt)), total

    def _filtered(self, filters: TaskFilters, statuses: list[str] | None) -> Select[tuple[Task]]:
        stmt = select(Task)
        if statuses:
            stmt = stmt.where(Task.status.in_(statuses))
        elif filters.status is not None:
            stmt = stmt.where(Task.status == filters.status)
        if filters.priority is not None:
            stmt = stmt.where(Task.priority == TaskPriority(filters.priority))
        if filters.tag:
            stmt = stmt.where(Task.tags.any(Tag.name == filters.tag))
        return stmt

    @staticmethod
    def _ordered(stmt: Select[tuple[Task]], filters: TaskFilters) -> Select[tuple[Task]]:
        descending = filters.order == "desc"
        if filters.sort == "due_at":
            # Tasks without a due date always go last, whatever the direction.
            column = Task.due_at.desc() if descending else Task.due_at.asc()
            return stmt.order_by(Task.due_at.is_(None), column, Task.id)
        if filters.sort == "priority":
            column = _PRIORITY_ORDER.desc() if descending else _PRIORITY_ORDER.asc()
            # Within a priority, the most urgent due date first.
            return stmt.order_by(column, Task.due_at.is_(None), Task.due_at.asc(), Task.id)
        sort_column = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "title": func.lower(Task.title),
        }[filters.sort]
        tiebreak = Task.id.desc() if descending else Task.id.asc()
        return stmt.order_by(sort_column.desc() if descending else sort_column.asc(), tiebreak)

    # --- reminder queries -----------------------------------------------------------------

    def _open_with_due_date(self) -> Select[tuple[Task]]:
        return select(Task).where(Task.status != TaskStatus.DONE, Task.due_at.is_not(None))

    def _page(self, stmt: Select[tuple[Task]], page: PageParams) -> tuple[list[Task], int]:
        total = self.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = self.session.scalars(stmt.offset(page.offset).limit(page.page_size))
        return list(items), total

    def find_due_between(
        self, start: datetime, end: datetime, page: PageParams
    ) -> tuple[list[Task], int]:
        stmt = (
            self._open_with_due_date()
            .where(Task.due_at >= start, Task.due_at <= end)
            .order_by(Task.due_at.asc(), Task.id)
        )
        return self._page(stmt, page)

    def find_overdue(self, now: datetime, page: PageParams) -> tuple[list[Task], int]:
        stmt = (
            self._open_with_due_date().where(Task.due_at < now).order_by(Task.due_at.asc(), Task.id)
        )
        return self._page(stmt, page)

    def _notifications(self, now: datetime) -> Select[tuple[Task]]:
        # Same rule as reminder_rules.needs_notification, expressed in SQL.
        return self._open_with_due_date().where(
            Task.due_at <= now,
            or_(Task.reminder_dismissed_at.is_(None), Task.reminder_dismissed_at < Task.due_at),
        )

    def find_notifications(self, now: datetime, page: PageParams) -> tuple[list[Task], int]:
        stmt = self._notifications(now).order_by(Task.due_at.desc(), Task.id.desc())
        return self._page(stmt, page)

    def all_notifications(self, now: datetime) -> list[Task]:
        return list(self.session.scalars(self._notifications(now)))
