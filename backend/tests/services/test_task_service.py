from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from app.models import TaskStatus
from app.repositories.tag_repository import TagRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.tag_service import TagService
from app.services.task_service import TaskService
from tests.conftest import FIXED_NOW, FixedClock


@pytest.fixture
def service(db: Session, clock: FixedClock) -> TaskService:
    return TaskService(db, TaskRepository(db), TagService(db, TagRepository(db)), clock)


def test_changing_due_date_resets_dismissal(service: TaskService) -> None:
    task = service.create(TaskCreate(title="t", due_at=FIXED_NOW))
    task.reminder_dismissed_at = FIXED_NOW
    service.update(task.id, TaskUpdate(due_at=FIXED_NOW + timedelta(days=1)))
    assert task.reminder_dismissed_at is None


def test_same_due_date_keeps_dismissal(service: TaskService) -> None:
    task = service.create(TaskCreate(title="t", due_at=FIXED_NOW))
    task.reminder_dismissed_at = FIXED_NOW
    service.update(task.id, TaskUpdate(due_at=FIXED_NOW, title="renamed"))
    assert task.reminder_dismissed_at == FIXED_NOW


def test_completion_timestamp_follows_status(service: TaskService, clock: FixedClock) -> None:
    task = service.create(TaskCreate(title="t"))
    assert task.completed_at is None
    clock.advance(minutes=5)
    service.update(task.id, TaskUpdate(status=TaskStatus.DONE))
    assert task.completed_at == FIXED_NOW + timedelta(minutes=5)
    service.update(task.id, TaskUpdate(status=TaskStatus.IN_PROGRESS))
    assert task.completed_at is None


def test_to_read_computes_reminder_flags(service: TaskService) -> None:
    task = service.create(TaskCreate(title="t", due_at=FIXED_NOW + timedelta(hours=47)))
    read = service.to_read(task)
    assert read.is_due_soon is True
    assert read.is_overdue is False
