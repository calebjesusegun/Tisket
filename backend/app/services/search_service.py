"""Search across tasks and notes, returning highlight segments instead of HTML."""

import re

from app.core.clock import Clock
from app.models import Note, Task
from app.repositories.search_repository import START_SEL, STOP_SEL, SearchHit, SearchRepository
from app.schemas.common import Page, PageParams
from app.schemas.search import HighlightSegment, SearchResult, SearchType
from app.schemas.tag import TagRead

SNIPPET_RADIUS = 80
MAX_TERMS = 8
_WORD = re.compile(r"\w+", re.UNICODE)
_MARKED = re.compile(f"{START_SEL}(.*?){STOP_SEL}", re.DOTALL)


def query_terms(q: str) -> list[str]:
    """Split a free-text query into de-duplicated lower-case word terms (max 8)."""
    return list(dict.fromkeys(t.lower() for t in _WORD.findall(q)))[:MAX_TERMS]


def segments_from_markers(text: str) -> list[HighlightSegment]:
    """Parse ts_headline output with START_SEL/STOP_SEL markers into segments."""
    segments: list[HighlightSegment] = []
    position = 0
    for marked in _MARKED.finditer(text):
        if marked.start() > position:
            segments.append(HighlightSegment(text=text[position : marked.start()], match=False))
        segments.append(HighlightSegment(text=marked.group(1), match=True))
        position = marked.end()
    if position < len(text):
        segments.append(HighlightSegment(text=text[position:], match=False))
    return _merge(segments)


def segments_from_terms(text: str, terms: list[str]) -> list[HighlightSegment]:
    """Highlight every case-insensitive occurrence of any term."""
    if not text:
        return []
    if not terms:
        return [HighlightSegment(text=text, match=False)]
    pattern = re.compile("|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True)), re.I)
    segments: list[HighlightSegment] = []
    position = 0
    for found in pattern.finditer(text):
        if found.start() > position:
            segments.append(HighlightSegment(text=text[position : found.start()], match=False))
        segments.append(HighlightSegment(text=found.group(0), match=True))
        position = found.end()
    if position < len(text):
        segments.append(HighlightSegment(text=text[position:], match=False))
    return _merge(segments)


def snippet_around_first_match(text: str, terms: list[str], radius: int = SNIPPET_RADIUS) -> str:
    """A short excerpt centred on the first matching term (or the start of the text)."""
    text = " ".join(text.split())
    lowered = text.lower()
    positions = [p for p in (lowered.find(t) for t in terms) if p >= 0]
    if not positions:
        return text[: radius * 2] + ("…" if len(text) > radius * 2 else "")
    first = min(positions)
    start = max(0, first - radius)
    end = min(len(text), first + radius)
    if start > 0:
        space = text.rfind(" ", 0, start)
        start = space + 1 if space != -1 else start
    if end < len(text):
        space = text.find(" ", end)
        end = space if space != -1 else len(text)
    return ("…" if start > 0 else "") + text[start:end] + ("…" if end < len(text) else "")


def _merge(segments: list[HighlightSegment]) -> list[HighlightSegment]:
    merged: list[HighlightSegment] = []
    for seg in segments:
        if not seg.text:
            continue
        if merged and merged[-1].match == seg.match:
            merged[-1] = HighlightSegment(text=merged[-1].text + seg.text, match=seg.match)
        else:
            merged.append(seg)
    return merged


class SearchService:
    def __init__(self, repository: SearchRepository, clock: Clock) -> None:
        self.repository = repository
        self.clock = clock

    def search(self, q: str, type_: SearchType, page: PageParams) -> Page[SearchResult]:
        terms = query_terms(q)
        if not terms:
            return Page.build([], 0, page.page, page.page_size)
        types: list[str] = ["task", "note"] if type_ == "all" else [type_]
        hits, total = self.repository.search(terms, types, page.offset, page.page_size)
        tasks = self.repository.load_tasks([h.id for h in hits if h.type == "task"])
        notes = self.repository.load_notes([h.id for h in hits if h.type == "note"])
        results = []
        for hit in hits:
            if hit.type == "task" and hit.id in tasks:
                results.append(self._task_result(tasks[hit.id], hit, terms))
            elif hit.type == "note" and hit.id in notes:
                results.append(self._note_result(notes[hit.id], hit, terms))
        return Page.build(results, total, page.page, page.page_size)

    def _highlights(
        self, title: str, body: str, hit: SearchHit, terms: list[str]
    ) -> tuple[list[HighlightSegment], list[HighlightSegment]]:
        if hit.title_headline is not None and hit.body_headline is not None:
            return segments_from_markers(hit.title_headline), segments_from_markers(
                " ".join(hit.body_headline.split())
            )
        return (
            segments_from_terms(title, terms),
            segments_from_terms(snippet_around_first_match(body, terms), terms),
        )

    def _task_result(self, task: Task, hit: SearchHit, terms: list[str]) -> SearchResult:
        title_hl, snippet = self._highlights(task.title, task.description, hit, terms)
        return SearchResult(
            type="task",
            id=task.id,
            title=task.title,
            title_highlights=title_hl,
            snippet=snippet,
            tags=[TagRead.model_validate(t) for t in task.tags],
            updated_at=task.updated_at,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
        )

    def _note_result(self, note: Note, hit: SearchHit, terms: list[str]) -> SearchResult:
        title_hl, snippet = self._highlights(note.title, note.content, hit, terms)
        return SearchResult(
            type="note",
            id=note.id,
            title=note.title,
            title_highlights=title_hl,
            snippet=snippet,
            tags=[TagRead.model_validate(t) for t in note.tags],
            updated_at=note.updated_at,
            pinned=note.pinned,
        )
