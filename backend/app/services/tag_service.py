"""Tag rules: normalisation, validation and get-or-create ("tags on the fly")."""

import re
from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import BadRequestError, ConflictError, NotFoundError
from app.models import Tag
from app.models.tag import TAG_NAME_MAX_LENGTH
from app.repositories.tag_repository import TagRepository

_WHITESPACE = re.compile(r"\s+")
_VALID = re.compile(r"^[a-z0-9_-]+$")


def normalize_tag_name(raw: str) -> str:
    """'  Deep  Work ' -> 'deep-work'. Leading '#' is dropped so '#work' == 'work'."""
    name = _WHITESPACE.sub("-", raw.strip().lower().lstrip("#").strip())
    return name.strip("-")


class TagService:
    def __init__(self, session: Session, repository: TagRepository) -> None:
        self.session = session
        self.repository = repository

    def validate(self, raw: str) -> str:
        name = normalize_tag_name(raw)
        problem = None
        if not name:
            problem = "Tag name cannot be empty"
        elif len(name) > TAG_NAME_MAX_LENGTH:
            problem = f"Tag name must be at most {TAG_NAME_MAX_LENGTH} characters"
        elif not _VALID.match(name):
            problem = "Tag names may only contain letters, numbers, '-' and '_'"
        if problem:
            raise BadRequestError(
                f"Invalid tag '{raw}': {problem}",
                details=[{"field": "tags", "message": problem, "value": raw}],
            )
        return name

    def resolve(self, raw_names: Iterable[str]) -> list[Tag]:
        """Return Tag rows for the given names, creating any that do not exist yet."""
        names = list(dict.fromkeys(self.validate(raw) for raw in raw_names))
        existing = {tag.name: tag for tag in self.repository.get_by_names(names)}
        tags = []
        for name in names:
            tag = existing.get(name) or self.repository.add(Tag(name=name))
            tags.append(tag)
        return tags

    def list_tags(self) -> list[dict[str, Any]]:
        return self.repository.list_with_counts()

    def get(self, tag_id: int) -> Tag:
        tag = self.repository.get(tag_id)
        if tag is None:
            raise NotFoundError(f"Tag {tag_id} not found")
        return tag

    def create(self, raw_name: str) -> Tag:
        name = self.validate(raw_name)
        if self.repository.get_by_name(name):
            raise ConflictError(f"Tag '{name}' already exists")
        tag = self.repository.add(Tag(name=name))
        self.session.commit()
        return tag

    def rename(self, tag_id: int, raw_name: str) -> Tag:
        tag = self.get(tag_id)
        name = self.validate(raw_name)
        other = self.repository.get_by_name(name)
        if other is not None and other.id != tag.id:
            raise ConflictError(f"Tag '{name}' already exists")
        tag.name = name
        self.session.commit()
        return tag

    def delete(self, tag_id: int) -> None:
        self.repository.delete(self.get(tag_id))
        self.session.commit()
