from datetime import timedelta

import pytest

from app.models import Task, TaskStatus
from app.services import reminder_rules
from tests.conftest import FIXED_NOW

NOW = FIXED_NOW


def make(offset: timedelta | None, status: TaskStatus = TaskStatus.TODO) -> Task:
    return Task(title="t", status=status, due_at=None if offset is None else NOW + offset)


@pytest.mark.parametrize(
    ("offset", "status", "expected"),
    [
        (timedelta(seconds=-1), TaskStatus.TODO, True),
        (timedelta(days=-10), TaskStatus.IN_PROGRESS, True),
        (timedelta(0), TaskStatus.TODO, False),  # due exactly now is not yet overdue
        (timedelta(hours=1), TaskStatus.TODO, False),
        (timedelta(days=-1), TaskStatus.DONE, False),
        (None, TaskStatus.TODO, False),
    ],
)
def test_is_overdue(offset: timedelta | None, status: TaskStatus, expected: bool) -> None:
    assert reminder_rules.is_overdue(make(offset, status), NOW) is expected


@pytest.mark.parametrize(
    ("offset", "status", "expected"),
    [
        (timedelta(0), TaskStatus.TODO, True),
        (timedelta(hours=48), TaskStatus.TODO, True),  # window end is inclusive
        (timedelta(hours=48, seconds=1), TaskStatus.TODO, False),
        (timedelta(seconds=-1), TaskStatus.TODO, False),  # overdue, not "due soon"
        (timedelta(hours=1), TaskStatus.DONE, False),
        (None, TaskStatus.TODO, False),
    ],
)
def test_is_due_soon(offset: timedelta | None, status: TaskStatus, expected: bool) -> None:
    assert reminder_rules.is_due_soon(make(offset, status), NOW) is expected


def test_is_due_soon_custom_window() -> None:
    task = make(timedelta(hours=10))
    assert reminder_rules.is_due_soon(task, NOW, hours=12) is True
    assert reminder_rules.is_due_soon(task, NOW, hours=6) is False


def test_needs_notification() -> None:
    due = make(timedelta(minutes=-5))
    assert reminder_rules.needs_notification(due, NOW) is True

    due.reminder_dismissed_at = NOW
    assert reminder_rules.needs_notification(due, NOW) is False

    # Dismissed before the (new) due date -> notifies again.
    due.reminder_dismissed_at = NOW - timedelta(hours=1)
    assert reminder_rules.needs_notification(due, NOW) is True

    assert reminder_rules.needs_notification(make(timedelta(minutes=5)), NOW) is False
    assert reminder_rules.needs_notification(make(None), NOW) is False
    done = make(timedelta(minutes=-5), TaskStatus.DONE)
    assert reminder_rules.needs_notification(done, NOW) is False
