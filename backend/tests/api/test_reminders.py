from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from tests.conftest import FIXED_NOW, FixedClock
from tests.factories import create_task

URL = "/api/v1/reminders"


def iso(dt: datetime) -> str:
    return dt.isoformat()


def at(**delta: float) -> str:
    return iso(FIXED_NOW + timedelta(**delta))


def titles(body: dict[str, object]) -> list[str]:
    return [t["title"] for t in body["items"]]  # type: ignore[attr-defined]


def seed(client: TestClient) -> None:
    create_task(client, title="overdue-old", due_at=at(days=-3))
    create_task(client, title="overdue-new", due_at=at(minutes=-10))
    create_task(client, title="done-overdue", due_at=at(days=-1), status="done")
    create_task(client, title="soon", due_at=at(hours=2))
    create_task(client, title="edge-48h", due_at=at(hours=48))
    create_task(client, title="later", due_at=at(hours=49))
    create_task(client, title="no-date")


def test_due_soon_default_48h_window(client: TestClient) -> None:
    seed(client)
    body = client.get(f"{URL}/due-soon").json()
    assert titles(body) == ["soon", "edge-48h"]
    assert all(t["is_due_soon"] for t in body["items"])


def test_due_soon_custom_window_and_pagination(client: TestClient) -> None:
    seed(client)
    assert titles(client.get(f"{URL}/due-soon", params={"hours": 72}).json()) == [
        "soon",
        "edge-48h",
        "later",
    ]
    page = client.get(f"{URL}/due-soon", params={"page_size": 1, "page": 2}).json()
    assert titles(page) == ["edge-48h"]
    assert page["total"] == 2


def test_due_soon_validation(client: TestClient) -> None:
    assert client.get(f"{URL}/due-soon", params={"hours": 0}).status_code == 422
    assert client.get(f"{URL}/due-soon", params={"hours": 169}).status_code == 422


def test_overdue(client: TestClient) -> None:
    seed(client)
    body = client.get(f"{URL}/overdue").json()
    assert titles(body) == ["overdue-old", "overdue-new"]
    assert all(t["is_overdue"] for t in body["items"])


def test_notifications_list_due_tasks(client: TestClient) -> None:
    seed(client)
    body = client.get(f"{URL}/notifications").json()
    assert titles(body) == ["overdue-new", "overdue-old"]
    assert body["total"] == 2


def test_notification_appears_when_task_becomes_due(client: TestClient, clock: FixedClock) -> None:
    create_task(client, title="soon", due_at=at(minutes=30))
    assert client.get(f"{URL}/notifications").json()["total"] == 0
    clock.advance(minutes=30)
    assert titles(client.get(f"{URL}/notifications").json()) == ["soon"]


def test_dismiss_notification(client: TestClient, clock: FixedClock) -> None:
    task = create_task(client, title="due", due_at=at(minutes=-1))
    response = client.post(f"{URL}/{task['id']}/dismiss")
    assert response.status_code == 200
    assert response.json()["id"] == task["id"]
    assert client.get(f"{URL}/notifications").json()["total"] == 0
    # Still overdue, just not notifying.
    assert titles(client.get(f"{URL}/overdue").json()) == ["due"]


def test_new_due_date_notifies_again_after_dismiss(client: TestClient, clock: FixedClock) -> None:
    task = create_task(client, title="due", due_at=at(minutes=-1))
    client.post(f"{URL}/{task['id']}/dismiss")
    client.patch(f"/api/v1/tasks/{task['id']}", json={"due_at": at(hours=1)})
    assert client.get(f"{URL}/notifications").json()["total"] == 0
    clock.advance(hours=1)
    assert titles(client.get(f"{URL}/notifications").json()) == ["due"]


def test_completing_task_clears_notification(client: TestClient) -> None:
    task = create_task(client, due_at=at(minutes=-1))
    client.patch(f"/api/v1/tasks/{task['id']}", json={"status": "done"})
    assert client.get(f"{URL}/notifications").json()["total"] == 0


def test_dismiss_missing_task(client: TestClient) -> None:
    response = client.post(f"{URL}/999/dismiss")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_dismiss_all(client: TestClient) -> None:
    seed(client)
    response = client.post(f"{URL}/dismiss-all")
    assert response.json() == {"dismissed": 2}
    assert client.get(f"{URL}/notifications").json()["total"] == 0
    assert client.post(f"{URL}/dismiss-all").json() == {"dismissed": 0}
