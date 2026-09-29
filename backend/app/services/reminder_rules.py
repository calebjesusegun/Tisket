"""Pure reminder rules shared by task responses and the reminders service."""

from datetime import datetime, timedelta

from app.models import Task, TaskStatus

DUE_SOON_HOURS = 48


def is_open(task: Task) -> bool:
    return task.status != TaskStatus.DONE


def is_overdue(task: Task, now: datetime) -> bool:
    return is_open(task) and task.due_at is not None and task.due_at < now


def is_due_soon(task: Task, now: datetime, hours: int = DUE_SOON_HOURS) -> bool:
    return (
        is_open(task)
        and task.due_at is not None
        and now <= task.due_at <= now + timedelta(hours=hours)
    )


def needs_notification(task: Task, now: datetime) -> bool:
    """A task notifies once it is due, until it is done or dismissed after becoming due."""
    if not is_open(task) or task.due_at is None or task.due_at > now:
        return False
    dismissed = task.reminder_dismissed_at
    return dismissed is None or dismissed < task.due_at
