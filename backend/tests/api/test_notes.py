import pytest
from fastapi.testclient import TestClient

from tests.conftest import FixedClock
from tests.factories import create_note, create_task

URL = "/api/v1/notes"


def test_create_note_minimal(client: TestClient) -> None:
    response = client.post(URL, json={"title": " Ideas "})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Ideas"
    assert body["content"] == ""
    assert body["pinned"] is False
    assert body["task_id"] is None
    assert body["task"] is None
    assert body["tags"] == []


def test_create_note_with_markdown_tags_and_task(client: TestClient) -> None:
    task = create_task(client, title="Launch")
    body = create_note(
        client,
        title="Launch plan",
        content="# Plan\n\n- [x] draft\n- [ ] ship",
        pinned=True,
        task_id=task["id"],
        tags=["Project", "launch"],
    )
    assert body["content"].startswith("# Plan")
    assert body["pinned"] is True
    assert body["task"] == {"id": task["id"], "title": "Launch", "status": "todo"}
    assert [t["name"] for t in body["tags"]] == ["launch", "project"]


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({}, "title"),
        ({"title": ""}, "title"),
        ({"title": "x" * 201}, "title"),
        ({"title": "ok", "content": "x" * 20001}, "content"),
        ({"title": "ok", "pinned": "maybe"}, "pinned"),
        ({"title": "ok", "task_id": 0}, "task_id"),
    ],
)
def test_create_note_validation(client: TestClient, payload: dict[str, object], field: str) -> None:
    response = client.post(URL, json=payload)
    assert response.status_code == 422
    assert any(d["field"] == field for d in response.json()["error"]["details"])


def test_create_note_with_unknown_task(client: TestClient) -> None:
    response = client.post(URL, json={"title": "x", "task_id": 999})
    assert response.status_code == 400
    assert response.json()["error"]["details"] == [
        {"field": "task_id", "message": "Task not found"}
    ]


def test_create_note_with_invalid_tag(client: TestClient) -> None:
    assert client.post(URL, json={"title": "x", "tags": ["a b c!"]}).status_code == 400


def test_get_note_and_404(client: TestClient) -> None:
    note = create_note(client)
    assert client.get(f"{URL}/{note['id']}").json() == note
    missing = client.get(f"{URL}/999")
    assert missing.status_code == 404
    assert missing.json()["error"]["message"] == "Note 999 not found"


def test_update_note(client: TestClient, clock: FixedClock) -> None:
    note = create_note(client, content="old", tags=["a"])
    task = create_task(client)
    response = client.patch(
        f"{URL}/{note['id']}",
        json={"content": "new **bold**", "pinned": True, "task_id": task["id"], "tags": ["b"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "new **bold**"
    assert body["pinned"] is True
    assert body["task"]["id"] == task["id"]
    assert [t["name"] for t in body["tags"]] == ["b"]
    assert body["title"] == note["title"]


def test_unlink_task_from_note(client: TestClient) -> None:
    task = create_task(client)
    note = create_note(client, task_id=task["id"])
    body = client.patch(f"{URL}/{note['id']}", json={"task_id": None}).json()
    assert body["task_id"] is None
    assert body["task"] is None


@pytest.mark.parametrize(
    "payload", [{"title": ""}, {"title": None}, {"pinned": None}, {"content": None}]
)
def test_update_note_validation(client: TestClient, payload: dict[str, object]) -> None:
    note = create_note(client)
    assert client.patch(f"{URL}/{note['id']}", json=payload).status_code == 422


def test_update_note_errors(client: TestClient) -> None:
    note = create_note(client)
    assert client.patch(f"{URL}/999", json={"title": "x"}).status_code == 404
    assert client.patch(f"{URL}/{note['id']}", json={"task_id": 999}).status_code == 400
    assert client.patch(f"{URL}/{note['id']}", json={"tags": ["!!"]}).status_code == 400


def test_delete_note(client: TestClient) -> None:
    note = create_note(client)
    assert client.delete(f"{URL}/{note['id']}").status_code == 204
    assert client.get(f"{URL}/{note['id']}").status_code == 404
    assert client.delete(f"{URL}/{note['id']}").status_code == 404


def test_deleting_task_unlinks_notes(client: TestClient) -> None:
    task = create_task(client)
    note = create_note(client, task_id=task["id"])
    assert client.delete(f"/api/v1/tasks/{task['id']}").status_code == 204
    body = client.get(f"{URL}/{note['id']}").json()
    assert body["task_id"] is None
    assert body["task"] is None


def test_list_notes_pinned_first_then_recent(client: TestClient, clock: FixedClock) -> None:
    create_note(client, title="old")
    clock.advance(minutes=1)
    create_note(client, title="pinned-old", pinned=True)
    clock.advance(minutes=1)
    create_note(client, title="new")
    body = client.get(URL).json()
    assert [n["title"] for n in body["items"]] == ["pinned-old", "new", "old"]
    assert body["total"] == 3


def test_list_notes_filters_and_pagination(client: TestClient) -> None:
    task = create_task(client)
    create_note(client, title="a", tags=["work"], task_id=task["id"])
    create_note(client, title="b", tags=["home"], pinned=True)
    create_note(client, title="c", tags=["work"])

    def get(**params: object) -> list[str]:
        return sorted(n["title"] for n in client.get(URL, params=params).json()["items"])

    assert get(tag="Work") == ["a", "c"]
    assert get(pinned=True) == ["b"]
    assert get(pinned=False) == ["a", "c"]
    assert get(task_id=task["id"]) == ["a"]
    page = client.get(URL, params={"page_size": 2, "page": 2}).json()
    assert page["pages"] == 2
    assert len(page["items"]) == 1


def test_list_notes_invalid_query(client: TestClient) -> None:
    assert client.get(URL, params={"task_id": 0}).status_code == 422
    assert client.get(URL, params={"pinned": "perhaps"}).status_code == 422
    assert client.get(URL, params={"page_size": 500}).status_code == 422


def test_tag_counts_include_notes(client: TestClient) -> None:
    create_note(client, tags=["work"])
    create_task(client, tags=["work"])
    assert client.get("/api/v1/tags").json()[0] == {
        "id": 1,
        "name": "work",
        "task_count": 1,
        "note_count": 1,
    }
