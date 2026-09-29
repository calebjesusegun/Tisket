"""Reminder rules: overdue tasks, the "due soon" window and in-app notifications."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.clock import Clock
from app.core.errors import NotFoundError
from app.models import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.common import Page, PageParams
from app.schemas.task import TaskRead
from app.services.reminder_rules import DUE_SOON_HOURS
from app.services.task_service import task_to_read


class ReminderService:
    def __init__(self, session: Session, repository: TaskRepository, clock: Clock) -> None:
        self.session = session
        self.repository = repository
        self.clock = clock

    def _page(self, items: list[Task], total: int, page: PageParams) -> Page[TaskRead]:
        now = self.clock.now()
        return Page.build([task_to_read(t, now) for t in items], total, page.page, page.page_size)

    def due_soon(self, page: PageParams, hours: int = DUE_SOON_HOURS) -> Page[TaskRead]:
        """Open tasks due between now and now + `hours` (inclusive), soonest first."""
        now = self.clock.now()
        items, total = self.repository.find_due_between(now, now + timedelta(hours=hours), page)
        return self._page(items, total, page)

    def overdue(self, page: PageParams) -> Page[TaskRead]:
        """Open tasks whose due time has passed, most overdue first."""
        items, total = self.repository.find_overdue(self.clock.now(), page)
        return self._page(items, total, page)

    def notifications(self, page: PageParams) -> Page[TaskRead]:
        """Open tasks that are due and have not been dismissed since they became due."""
        items, total = self.repository.find_notifications(self.clock.now(), page)
        return self._page(items, total, page)

    def dismiss(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise NotFoundError(f"Task {task_id} not found")
        task.reminder_dismissed_at = self.clock.now()
        self.session.commit()
        return task

    def dismiss_all(self) -> int:
        now = self.clock.now()
        tasks = self.repository.all_notifications(now)
        for task in tasks:
            task.reminder_dismissed_at = now
        self.session.commit()
        return len(tasks)
