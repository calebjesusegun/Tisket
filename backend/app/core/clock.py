"""An injectable clock so time-dependent rules (reminders, overdue) are testable."""

from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


def utcnow() -> datetime:
    return datetime.now(UTC)
