import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError
from app.models import Tag
from app.repositories.tag_repository import TagRepository
from app.services.tag_service import TagService, normalize_tag_name


@pytest.fixture
def service(db: Session) -> TagService:
    return TagService(db, TagRepository(db))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Work", "work"),
        ("  work  ", "work"),
        ("Deep   Work", "deep-work"),
        ("#urgent", "urgent"),
        ("-edge-", "edge"),
        ("snake_case", "snake_case"),
        ("", ""),
    ],
)
def test_normalize_tag_name(raw: str, expected: str) -> None:
    assert normalize_tag_name(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "#", "a/b", "ça", "x" * 31])
def test_validate_rejects_bad_names(service: TagService, raw: str) -> None:
    with pytest.raises(BadRequestError) as excinfo:
        service.validate(raw)
    assert excinfo.value.details
    assert excinfo.value.details[0]["field"] == "tags"


def test_validate_accepts_max_length(service: TagService) -> None:
    assert service.validate("x" * 30) == "x" * 30


def test_resolve_creates_missing_and_reuses_existing(service: TagService, db: Session) -> None:
    first = service.resolve(["Work", "home"])
    db.commit()
    second = service.resolve(["work", "HOME", "new"])
    db.commit()
    assert [t.name for t in first] == ["work", "home"]
    assert [t.name for t in second] == ["work", "home", "new"]
    assert first[0].id == second[0].id
    assert db.scalar(select(func.count()).select_from(Tag)) == 3


def test_resolve_deduplicates_and_keeps_order(service: TagService) -> None:
    tags = service.resolve(["b", "a", "B", " a "])
    assert [t.name for t in tags] == ["b", "a"]


def test_resolve_empty_list(service: TagService) -> None:
    assert service.resolve([]) == []


def test_resolve_is_all_or_nothing_on_invalid_name(service: TagService, db: Session) -> None:
    with pytest.raises(BadRequestError):
        service.resolve(["good", "bad name!"])
    db.rollback()
    assert db.scalar(select(func.count()).select_from(Tag)) == 0
