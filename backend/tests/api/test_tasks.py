from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from tests.conftest import FIXED_NOW, FixedClock
from tests.factories import create_task

URL = "/api/v1/tasks"


def iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


# --- create --------------------------------------------------------------------------------


def test_create_task_with_defaults(client: TestClient) -> None:
    response = client.post(URL, json={"title": "  Buy milk  "})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["description"] == ""
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["due_at"] is None
    assert body["completed_at"] is None
    assert body["tags"] == []
    assert body["is_overdue"] is False
    assert body["is_due_soon"] is False
    assert isinstance(body["id"], int)


def test_create_task_with_all_fields_and_new_tags(client: TestClient) -> None:
    due = FIXED_NOW + timedelta(hours=5)
    body = create_task(
        client,
        title="Write report",
        description="Quarterly numbers",
        priority="high",
        status="in_progress",
        due_at=iso(due),
        tags=["Work", " work ", "Deep Work"],
    )
    assert body["priority"] == "high"
    assert body["status"] == "in_progress"
    assert datetime.fromisoformat(body["due_at"]) == due
    assert [t["name"] for t in body["tags"]] == ["deep-work", "work"]
    assert body["is_due_soon"] is True


def test_create_done_task_sets_completed_at(client: TestClient) -> None:
    body = create_task(client, status="done")
    assert datetime.fromisoformat(body["completed_at"]) == FIXED_NOW


def test_naive_due_date_is_treated_as_utc(client: TestClient) -> None:
    body = create_task(client, due_at="2026-02-01T09:30:00")
    assert datetime.fromisoformat(body["due_at"]) == datetime(2026, 2, 1, 9, 30, tzinfo=UTC)


def test_offset_due_date_is_converted_to_utc(client: TestClient) -> None:
    body = create_task(client, due_at="2026-02-01T10:30:00+01:00")
    assert datetime.fromisoformat(body["due_at"]) == datetime(2026, 2, 1, 9, 30, tzinfo=UTC)


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({}, "title"),
        ({"title": "   "}, "title"),
        ({"title": "x" * 201}, "title"),
        ({"title": "ok", "priority": "urgent"}, "priority"),
        ({"title": "ok", "status": "blocked"}, "status"),
        ({"title": "ok", "due_at": "not-a-date"}, "due_at"),
        ({"title": "ok", "description": "x" * 5001}, "description"),
        ({"title": "ok", "tags": [f"t{i}" for i in range(11)]}, "tags"),
    ],
)
def test_create_task_validation_errors(
    client: TestClient, payload: dict[str, object], field: str
) -> None:
    response = client.post(URL, json=payload)
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert any(d["field"] == field for d in error["details"]), error


def test_create_task_rejects_invalid_tag_name(client: TestClient) -> None:
    response = client.post(URL, json={"title": "ok", "tags": ["no/slashes"]})
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "bad_request"
    assert error["details"][0]["field"] == "tags"


# --- read ----------------------------------------------------------------------------------


def test_get_task(client: TestClient) -> None:
    created = create_task(client, title="Read me")
    response = client.get(f"{URL}/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_task_returns_404(client: TestClient) -> None:
    response = client.get(f"{URL}/999")
    assert response.status_code == 404
    assert response.json()["error"] == {
        "code": "not_found",
        "message": "Task 999 not found",
        "details": None,
    }


def test_get_task_with_invalid_id_returns_422(client: TestClient) -> None:
    assert client.get(f"{URL}/abc").status_code == 422


# --- update --------------------------------------------------------------------------------


def test_update_task_partially(client: TestClient) -> None:
    created = create_task(client, title="Old", description="keep me", tags=["a"])
    response = client.patch(f"{URL}/{created['id']}", json={"title": "New", "priority": "low"})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "New"
    assert body["priority"] == "low"
    assert body["description"] == "keep me"
    assert [t["name"] for t in body["tags"]] == ["a"]


def test_mark_complete_and_reopen(client: TestClient, clock: FixedClock) -> None:
    task = create_task(client)
    clock.advance(hours=1)
    done = client.patch(f"{URL}/{task['id']}", json={"status": "done"}).json()
    assert done["status"] == "done"
    assert datetime.fromisoformat(done["completed_at"]) == FIXED_NOW + timedelta(hours=1)

    clock.advance(hours=1)
    # Saving a done task again keeps the original completion time.
    again = client.patch(f"{URL}/{task['id']}", json={"title": "Renamed"}).json()
    assert again["completed_at"] == done["completed_at"]

    reopened = client.patch(f"{URL}/{task['id']}", json={"status": "todo"}).json()
    assert reopened["completed_at"] is None


def test_update_replaces_tags_and_clears_due_date(client: TestClient) -> None:
    task = create_task(client, tags=["a", "b"], due_at=iso(FIXED_NOW + timedelta(days=1)))
    body = client.patch(f"{URL}/{task['id']}", json={"tags": ["c"], "due_at": None}).json()
    assert [t["name"] for t in body["tags"]] == ["c"]
    assert body["due_at"] is None


def test_update_with_empty_body_changes_nothing(client: TestClient) -> None:
    task = create_task(client, title="Same")
    body = client.patch(f"{URL}/{task['id']}", json={}).json()
    assert body["title"] == "Same"


@pytest.mark.parametrize(
    "payload",
    [{"title": ""}, {"title": None}, {"status": None}, {"priority": "x"}, {"tags": None}],
)
def test_update_validation_errors(client: TestClient, payload: dict[str, object]) -> None:
    task = create_task(client)
    response = client.patch(f"{URL}/{task['id']}", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_update_missing_task_returns_404(client: TestClient) -> None:
    assert client.patch(f"{URL}/999", json={"title": "x"}).status_code == 404


def test_update_with_invalid_tag_returns_400(client: TestClient) -> None:
    task = create_task(client)
    assert client.patch(f"{URL}/{task['id']}", json={"tags": ["bad tag!"]}).status_code == 400


# --- delete --------------------------------------------------------------------------------


def test_delete_task(client: TestClient) -> None:
    task = create_task(client, tags=["keep"])
    response = client.delete(f"{URL}/{task['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"{URL}/{task['id']}").status_code == 404
    # The tag itself survives; only the link is removed.
    tags = client.get("/api/v1/tags").json()
    assert tags == [{"id": tags[0]["id"], "name": "keep", "task_count": 0, "note_count": 0}]


def test_delete_missing_task_returns_404(client: TestClient) -> None:
    assert client.delete(f"{URL}/999").status_code == 404


# --- list: pagination, filters, sorting ------------------------------------------------------


def titles(response_json: dict[str, object]) -> list[str]:
    return [item["title"] for item in response_json["items"]]  # type: ignore[attr-defined]


def test_list_is_paginated(client: TestClient) -> None:
    for i in range(5):
        create_task(client, title=f"Task {i}")
    first = client.get(URL, params={"page": 1, "page_size": 2}).json()
    assert first["total"] == 5
    assert first["pages"] == 3
    assert first["page"] == 1
    assert first["page_size"] == 2
    assert titles(first) == ["Task 4", "Task 3"]  # newest first by default
    last = client.get(URL, params={"page": 3, "page_size": 2}).json()
    assert titles(last) == ["Task 0"]
    beyond = client.get(URL, params={"page": 9, "page_size": 2}).json()
    assert beyond["items"] == []


def test_empty_list(client: TestClient) -> None:
    body = client.get(URL).json()
    assert body == {"items": [], "total": 0, "page": 1, "page_size": 20, "pages": 0}


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page_size": 0},
        {"page_size": 101},
        {"status": "nope"},
        {"priority": "nope"},
        {"sort": "nope"},
        {"order": "sideways"},
    ],
)
def test_list_rejects_invalid_query(client: TestClient, params: dict[str, object]) -> None:
    response = client.get(URL, params=params)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_filter_by_status_priority_and_tag(client: TestClient) -> None:
    create_task(client, title="a", status="todo", priority="high", tags=["work"])
    create_task(client, title="b", status="in_progress", priority="high", tags=["home"])
    create_task(client, title="c", status="done", priority="low", tags=["work"])

    def get(**params: object) -> list[str]:
        return sorted(titles(client.get(URL, params=params).json()))

    assert get(status="todo") == ["a"]
    assert get(status=["todo", "in_progress"]) == ["a", "b"]
    assert get(priority="high") == ["a", "b"]
    assert get(tag="work") == ["a", "c"]
    assert get(tag="WORK") == ["a", "c"]  # tag filter is normalised
    assert get(tag="work", priority="high") == ["a"]
    assert get(tag="unknown") == []


def test_sort_by_due_date_puts_undated_last(client: TestClient) -> None:
    create_task(client, title="none")
    create_task(client, title="later", due_at=iso(FIXED_NOW + timedelta(days=3)))
    create_task(client, title="sooner", due_at=iso(FIXED_NOW + timedelta(days=1)))
    asc = client.get(URL, params={"sort": "due_at", "order": "asc"}).json()
    desc = client.get(URL, params={"sort": "due_at", "order": "desc"}).json()
    assert titles(asc) == ["sooner", "later", "none"]
    assert titles(desc) == ["later", "sooner", "none"]


def test_sort_by_priority(client: TestClient) -> None:
    create_task(client, title="low", priority="low")
    create_task(client, title="high", priority="high")
    create_task(client, title="medium", priority="medium")
    desc = client.get(URL, params={"sort": "priority", "order": "desc"}).json()
    asc = client.get(URL, params={"sort": "priority", "order": "asc"}).json()
    assert titles(desc) == ["high", "medium", "low"]
    assert titles(asc) == ["low", "medium", "high"]


def test_sort_by_title_and_created(client: TestClient) -> None:
    create_task(client, title="banana")
    create_task(client, title="Apple")
    create_task(client, title="cherry")
    by_title = client.get(URL, params={"sort": "title", "order": "asc"}).json()
    assert titles(by_title) == ["Apple", "banana", "cherry"]
    oldest = client.get(URL, params={"sort": "created_at", "order": "asc"}).json()
    assert titles(oldest) == ["banana", "Apple", "cherry"]
    by_updated = client.get(URL, params={"sort": "updated_at", "order": "desc"}).json()
    assert len(by_updated["items"]) == 3


def test_overdue_flag(client: TestClient) -> None:
    overdue = create_task(client, due_at=iso(FIXED_NOW - timedelta(minutes=1)))
    done = create_task(client, status="done", due_at=iso(FIXED_NOW - timedelta(days=1)))
    far = create_task(client, due_at=iso(FIXED_NOW + timedelta(days=5)))
    assert overdue["is_overdue"] is True
    assert overdue["is_due_soon"] is False
    assert done["is_overdue"] is False
    assert far["is_overdue"] is False
    assert far["is_due_soon"] is False
