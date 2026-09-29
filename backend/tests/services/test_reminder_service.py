from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models import Task, TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.common import PageParams
from app.services.reminder_service import ReminderService
from tests.conftest import FIXED_NOW, FixedClock

PAGE = PageParams(page=1, page_size=50)


@pytest.fixture
def service(db: Session, clock: FixedClock) -> ReminderService:
    return ReminderService(db, TaskRepository(db), clock)


def add(db: Session, title: str, offset: timedelta | None, **kwargs: object) -> Task:
    task = Task(title=title, due_at=None if offset is None else FIXED_NOW + offset, **kwargs)
    db.add(task)
    db.commit()
    return task


def names(page: object) -> list[str]:
    return [t.title for t in page.items]  # type: ignore[attr-defined]


def test_due_soon_window_boundaries(service: ReminderService, db: Session) -> None:
    add(db, "now", timedelta(0))
    add(db, "end", timedelta(hours=48))
    add(db, "past", timedelta(seconds=-1))
    add(db, "after", timedelta(hours=48, seconds=1))
    add(db, "done", timedelta(hours=1), status=TaskStatus.DONE)
    assert names(service.due_soon(PAGE)) == ["now", "end"]
    assert names(service.due_soon(PAGE, hours=1)) == ["now"]


def test_overdue_excludes_done_and_undated(service: ReminderService, db: Session) -> None:
    add(db, "late", timedelta(hours=-1))
    add(db, "late-done", timedelta(hours=-1), status=TaskStatus.DONE)
    add(db, "undated", None)
    assert names(service.overdue(PAGE)) == ["late"]


def test_notifications_follow_the_clock(
    service: ReminderService, db: Session, clock: FixedClock
) -> None:
    add(db, "in-10-min", timedelta(minutes=10))
    assert names(service.notifications(PAGE)) == []
    clock.advance(minutes=10)
    assert names(service.notifications(PAGE)) == ["in-10-min"]


def test_dismiss_records_time_and_hides_notification(
    service: ReminderService, db: Session, clock: FixedClock
) -> None:
    task = add(db, "due", timedelta(minutes=-5))
    clock.advance(minutes=1)
    service.dismiss(task.id)
    assert task.reminder_dismissed_at == FIXED_NOW + timedelta(minutes=1)
    assert names(service.notifications(PAGE)) == []


def test_dismissal_before_due_date_does_not_hide(service: ReminderService, db: Session) -> None:
    add(db, "due", timedelta(minutes=-5), reminder_dismissed_at=FIXED_NOW - timedelta(hours=1))
    assert names(service.notifications(PAGE)) == ["due"]


def test_dismiss_unknown_task(service: ReminderService) -> None:
    with pytest.raises(NotFoundError):
        service.dismiss(12345)


def test_dismiss_all_only_touches_notifying_tasks(service: ReminderService, db: Session) -> None:
    due = add(db, "due", timedelta(minutes=-5))
    future = add(db, "future", timedelta(hours=5))
    assert service.dismiss_all() == 1
    assert due.reminder_dismissed_at == FIXED_NOW
    assert future.reminder_dismissed_at is None
