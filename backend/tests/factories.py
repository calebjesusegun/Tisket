"""Small helpers to create data through the API in tests."""

from typing import Any

from fastapi.testclient import TestClient


def create_task(client: TestClient, **fields: Any) -> dict[str, Any]:
    payload = {"title": "A task", **fields}
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201, response.text
    return response.json()  # type: ignore[no-any-return]


def create_note(client: TestClient, **fields: Any) -> dict[str, Any]:
    payload = {"title": "A note", **fields}
    response = client.post("/api/v1/notes", json=payload)
    assert response.status_code == 201, response.text
    return response.json()  # type: ignore[no-any-return]
