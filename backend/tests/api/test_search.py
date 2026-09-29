"""Search behaves the same on SQLite (LIKE fallback) and PostgreSQL (full-text search).

Assertions check that highlighted segments *contain* the query word, because PostgreSQL
highlights whole (stemmed) words while SQLite highlights the exact substring.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import FixedClock
from tests.factories import create_note, create_task

URL = "/api/v1/search"


def search(client: TestClient, **params: Any) -> dict[str, Any]:
    response = client.get(URL, params=params)
    assert response.status_code == 200, response.text
    return response.json()  # type: ignore[no-any-return]


def marked(segments: list[dict[str, Any]]) -> list[str]:
    return [s["text"].lower() for s in segments if s["match"]]


def plain(segments: list[dict[str, Any]]) -> str:
    return "".join(s["text"] for s in segments)


@pytest.fixture
def seeded(client: TestClient, clock: FixedClock) -> None:
    create_task(client, title="Buy groceries", description="Milk, eggs and bread", tags=["home"])
    clock.advance(minutes=1)
    create_task(client, title="Write quarterly report", description="Include grocery budget")
    clock.advance(minutes=1)
    create_note(
        client,
        title="Recipe ideas",
        content="Lasagna needs groceries: pasta, tomatoes and cheese. " + "Filler text. " * 20,
        tags=["cooking"],
    )
    clock.advance(minutes=1)
    create_note(client, title="Travel", content="Pack passport")


def test_search_finds_tasks_and_notes(client: TestClient, seeded: None) -> None:
    body = search(client, q="groceries")
    kinds = sorted((r["type"], r["title"]) for r in body["items"])
    assert ("task", "Buy groceries") in kinds
    assert ("note", "Recipe ideas") in kinds
    assert body["total"] == len(body["items"])


def test_title_matches_rank_first(client: TestClient, seeded: None) -> None:
    body = search(client, q="groceries")
    assert body["items"][0]["title"] == "Buy groceries"


def test_title_highlights(client: TestClient, seeded: None) -> None:
    result = next(r for r in search(client, q="groceries")["items"] if r["type"] == "task")
    assert plain(result["title_highlights"]) == "Buy groceries"
    assert any("groceries" in m for m in marked(result["title_highlights"]))
    assert result["tags"] == [{"id": result["tags"][0]["id"], "name": "home"}]
    assert result["status"] == "todo"
    assert result["priority"] == "medium"
    assert result["pinned"] is None


def test_snippet_highlights_body_match(client: TestClient, seeded: None) -> None:
    note = next(r for r in search(client, q="lasagna")["items"] if r["type"] == "note")
    assert any("lasagna" in m for m in marked(note["snippet"]))
    assert "" not in plain(note["snippet"])
    assert note["pinned"] is False
    assert note["status"] is None


def test_prefix_and_case_insensitive(client: TestClient, seeded: None) -> None:
    titles = {r["title"] for r in search(client, q="PASSP")["items"]}
    assert titles == {"Travel"}


def test_all_terms_must_match(client: TestClient, seeded: None) -> None:
    titles = {r["title"] for r in search(client, q="milk bread")["items"]}
    assert titles == {"Buy groceries"}
    assert search(client, q="milk passport")["items"] == []


def test_filter_by_type(client: TestClient, seeded: None) -> None:
    only_notes = search(client, q="groceries", type="note")
    assert {r["type"] for r in only_notes["items"]} == {"note"}
    only_tasks = search(client, q="groceries", type="task")
    assert {r["type"] for r in only_tasks["items"]} == {"task"}


def test_no_results(client: TestClient, seeded: None) -> None:
    body = search(client, q="zebra")
    assert body == {"items": [], "total": 0, "page": 1, "page_size": 20, "pages": 0}


def test_punctuation_only_query_returns_nothing(client: TestClient, seeded: None) -> None:
    assert search(client, q="!!!")["total"] == 0


def test_special_like_characters_are_literal(client: TestClient) -> None:
    create_task(client, title="snake_case naming")
    create_task(client, title="snakeXcase naming")
    titles = {r["title"] for r in search(client, q="snake_case")["items"]}
    assert "snake_case naming" in titles
    assert "snakeXcase naming" not in titles


def test_search_pagination(client: TestClient) -> None:
    for i in range(5):
        create_task(client, title=f"Alpha item {i}")
    first = search(client, q="alpha", page_size=2)
    assert first["total"] == 5
    assert first["pages"] == 3
    assert len(first["items"]) == 2
    last = search(client, q="alpha", page_size=2, page=3)
    assert len(last["items"]) == 1


@pytest.mark.parametrize(
    "params",
    [{}, {"q": ""}, {"q": "   "}, {"q": "x" * 201}, {"q": "ok", "type": "tag"}],
)
def test_search_validation(client: TestClient, params: dict[str, Any]) -> None:
    response = client.get(URL, params=params)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
