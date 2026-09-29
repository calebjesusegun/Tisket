from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.dependencies import get_db


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "version": "0.1.0"}


def test_health_reports_database_unavailable(app: FastAPI) -> None:
    class BrokenSession:
        def execute(self, *_args: object) -> None:
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    app.dependency_overrides[get_db] = lambda: BrokenSession()
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["database"] == "unavailable"


def test_openapi_docs_available(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "Tisket API"
    assert "/health" in schema["paths"]


def test_db_fixture_shares_app_database(db: Session) -> None:
    assert db.bind is not None
