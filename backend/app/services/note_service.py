"""Note rules: optional link to an existing task, tags on the fly, pinned notes first."""

from sqlalchemy.orm import Session

from app.core.errors import BadRequestError, NotFoundError
from app.models import Note, Tag
from app.repositories.note_repository import NoteRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.common import Page, PageParams
from app.schemas.note import NoteCreate, NoteFilters, NoteRead, NoteUpdate
from app.services.tag_service import TagService, normalize_tag_name


class NoteService:
    def __init__(
        self,
        session: Session,
        repository: NoteRepository,
        task_repository: TaskRepository,
        tag_service: TagService,
    ) -> None:
        self.session = session
        self.repository = repository
        self.task_repository = task_repository
        self.tag_service = tag_service

    def get(self, note_id: int) -> Note:
        note = self.repository.get(note_id)
        if note is None:
            raise NotFoundError(f"Note {note_id} not found")
        return note

    def list_notes(self, filters: NoteFilters, page: PageParams) -> Page[NoteRead]:
        if filters.tag:
            filters = filters.model_copy(update={"tag": normalize_tag_name(filters.tag)})
        items, total = self.repository.find(filters, page)
        return Page.build(
            [NoteRead.model_validate(n) for n in items], total, page.page, page.page_size
        )

    def create(self, data: NoteCreate) -> Note:
        self._check_task(data.task_id)
        note = Note(
            title=data.title,
            content=data.content,
            pinned=data.pinned,
            task_id=data.task_id,
            tags=self._tags(data.tags),
        )
        self.repository.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def update(self, note_id: int, data: NoteUpdate) -> Note:
        note = self.get(note_id)
        changes = data.model_dump(exclude_unset=True)
        if "task_id" in changes:
            self._check_task(changes["task_id"])
        if "tags" in changes:
            note.tags = self._tags(changes.pop("tags"))
        for field, value in changes.items():
            setattr(note, field, value)
        self.session.commit()
        self.session.refresh(note)
        return note

    def delete(self, note_id: int) -> None:
        self.repository.delete(self.get(note_id))
        self.session.commit()

    def _check_task(self, task_id: int | None) -> None:
        if task_id is not None and self.task_repository.get(task_id) is None:
            raise BadRequestError(
                f"Task {task_id} does not exist",
                details=[{"field": "task_id", "message": "Task not found"}],
            )

    def _tags(self, names: list[str]) -> list[Tag]:
        return sorted(self.tag_service.resolve(names), key=lambda tag: tag.name)
