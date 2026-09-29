from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import ConflictError, NotFoundError


def _add_failing_routes(app: FastAPI) -> None:
    @app.get("/boom-not-found")
    def boom_not_found() -> None:
        raise NotFoundError("Thing 1 not found")

    @app.get("/boom-conflict")
    def boom_conflict() -> None:
        raise ConflictError("Already exists", details=[{"field": "name", "message": "taken"}])

    @app.get("/boom-unhandled")
    def boom_unhandled() -> None:
        raise RuntimeError("secret internal detail")

    @app.get("/needs-int")
    def needs_int(value: int) -> int:
        return value


def test_unknown_route_returns_json_404(client: TestClient) -> None:
    response = client.get("/nope")
    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Not Found", "details": None}
    }


def test_method_not_allowed_is_consistent(client: TestClient) -> None:
    response = client.delete("/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


def test_app_errors_use_consistent_shape(app: FastAPI) -> None:
    _add_failing_routes(app)
    with TestClient(app) as client:
        not_found = client.get("/boom-not-found")
        conflict = client.get("/boom-conflict")
    assert not_found.status_code == 404
    assert not_found.json()["error"] == {
        "code": "not_found",
        "message": "Thing 1 not found",
        "details": None,
    }
    assert conflict.status_code == 409
    assert conflict.json()["error"]["details"] == [{"field": "name", "message": "taken"}]


def test_unhandled_errors_hide_internals(app: FastAPI) -> None:
    _add_failing_routes(app)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom-unhandled")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert "secret" not in body["error"]["message"]


def test_validation_errors_list_fields(app: FastAPI) -> None:
    _add_failing_routes(app)
    with TestClient(app) as client:
        response = client.get("/needs-int", params={"value": "abc"})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "query.value"
    assert error["message"].startswith("query.value:")


def test_cors_allows_configured_origin_only(client: TestClient) -> None:
    allowed = client.options(
        "/health",
        headers={"Origin": "https://tisket.example.com", "Access-Control-Request-Method": "GET"},
    )
    assert allowed.headers["access-control-allow-origin"] == "https://tisket.example.com"

    blocked = client.options(
        "/health",
        headers={"Origin": "https://evil.example.com", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in blocked.headers
