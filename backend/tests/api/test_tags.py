import pytest
from fastapi.testclient import TestClient

from tests.factories import create_task

URL = "/api/v1/tags"


def test_list_tags_empty(client: TestClient) -> None:
    assert client.get(URL).json() == []


def test_create_tag_normalises_name(client: TestClient) -> None:
    response = client.post(URL, json={"name": "  #Side Project "})
    assert response.status_code == 201
    assert response.json()["name"] == "side-project"


def test_create_duplicate_tag_conflicts(client: TestClient) -> None:
    client.post(URL, json={"name": "work"})
    response = client.post(URL, json={"name": "WORK"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


@pytest.mark.parametrize("name", ["bad/name", "emoji🙂", "a" * 31, "#"])
def test_create_tag_rejects_invalid_names(client: TestClient, name: str) -> None:
    response = client.post(URL, json={"name": name})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"


def test_create_tag_requires_name(client: TestClient) -> None:
    assert client.post(URL, json={}).status_code == 422
    assert client.post(URL, json={"name": ""}).status_code == 422


def test_list_tags_with_counts_sorted_by_name(client: TestClient) -> None:
    create_task(client, tags=["work", "urgent"])
    create_task(client, tags=["work"])
    client.post(URL, json={"name": "archive"})
    body = client.get(URL).json()
    assert [(t["name"], t["task_count"], t["note_count"]) for t in body] == [
        ("archive", 0, 0),
        ("urgent", 1, 0),
        ("work", 2, 0),
    ]


def test_rename_tag(client: TestClient) -> None:
    tag = client.post(URL, json={"name": "wrk"}).json()
    task = create_task(client, tags=["wrk"])
    response = client.patch(f"{URL}/{tag['id']}", json={"name": "Work"})
    assert response.status_code == 200
    assert response.json() == {"id": tag["id"], "name": "work"}
    updated = client.get(f"/api/v1/tasks/{task['id']}").json()
    assert [t["name"] for t in updated["tags"]] == ["work"]


def test_rename_tag_to_same_name_is_allowed(client: TestClient) -> None:
    tag = client.post(URL, json={"name": "work"}).json()
    assert client.patch(f"{URL}/{tag['id']}", json={"name": "Work"}).status_code == 200


def test_rename_tag_conflict(client: TestClient) -> None:
    client.post(URL, json={"name": "work"})
    other = client.post(URL, json={"name": "home"}).json()
    response = client.patch(f"{URL}/{other['id']}", json={"name": "work"})
    assert response.status_code == 409


def test_rename_missing_tag(client: TestClient) -> None:
    assert client.patch(f"{URL}/999", json={"name": "x"}).status_code == 404


def test_rename_tag_invalid(client: TestClient) -> None:
    tag = client.post(URL, json={"name": "work"}).json()
    assert client.patch(f"{URL}/{tag['id']}", json={"name": "bad name!"}).status_code == 400
    assert client.patch(f"{URL}/{tag['id']}", json={}).status_code == 422


def test_delete_tag_detaches_it_from_tasks(client: TestClient) -> None:
    task = create_task(client, tags=["temp", "keep"])
    tag_id = next(t["id"] for t in task["tags"] if t["name"] == "temp")
    assert client.delete(f"{URL}/{tag_id}").status_code == 204
    updated = client.get(f"/api/v1/tasks/{task['id']}").json()
    assert [t["name"] for t in updated["tags"]] == ["keep"]
    assert [t["name"] for t in client.get(URL).json()] == ["keep"]


def test_delete_missing_tag(client: TestClient) -> None:
    assert client.delete(f"{URL}/999").status_code == 404
