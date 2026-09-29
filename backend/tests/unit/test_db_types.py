from datetime import UTC, datetime, timedelta, timezone

from sqlalchemy.dialects import postgresql, sqlite

from app.db.types import UTCDateTime

LAGOS = timezone(timedelta(hours=1))


def test_bind_converts_to_utc() -> None:
    value = datetime(2026, 1, 1, 13, 0, tzinfo=LAGOS)
    result = UTCDateTime().process_bind_param(value, postgresql.dialect())
    assert result == datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    assert result is not None
    assert result.tzinfo == UTC


def test_bind_assumes_naive_values_are_utc() -> None:
    result = UTCDateTime().process_bind_param(datetime(2026, 1, 1, 12), sqlite.dialect())
    assert result == datetime(2026, 1, 1, 12, tzinfo=UTC)


def test_result_tags_naive_values_as_utc() -> None:
    result = UTCDateTime().process_result_value(datetime(2026, 1, 1, 12), sqlite.dialect())
    assert result is not None
    assert result.tzinfo == UTC


def test_result_converts_aware_values_to_utc() -> None:
    value = datetime(2026, 1, 1, 13, tzinfo=LAGOS)
    result = UTCDateTime().process_result_value(value, postgresql.dialect())
    assert result == datetime(2026, 1, 1, 12, tzinfo=UTC)


def test_none_passes_through() -> None:
    assert UTCDateTime().process_bind_param(None, sqlite.dialect()) is None
    assert UTCDateTime().process_result_value(None, sqlite.dialect()) is None
