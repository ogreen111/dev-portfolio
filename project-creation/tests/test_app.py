from pathlib import Path

import account_store
from fastapi.testclient import TestClient

from project_creation.app import AppServices, create_app
from project_creation.auth import AccountAuthenticator, SessionManager
from project_creation.config import Settings
from project_creation.repository import RunRepository


def build_client(tmp_path: Path) -> tuple[TestClient, SessionManager]:
    account_store.configure(state_dir=tmp_path / "accounts")
    account_store.add_user("owen", "password", role="admin", display_name="Owen")
    settings = Settings(
        host="127.0.0.1",
        port=8773,
        allow_remote=False,
        db_path=tmp_path / "state.db",
        cyber_specs_path="Proposals/Tech/Cyber/RFP Summary/Cyber Specs",
        planner_template_id="AHEqL4KIXU2P3AMIiuF3X4IAELH7",
        default_owner="ogreen@spectrumsi.com",
        session_secret="test-secret",
    )
    sessions = SessionManager(
        "test-secret", ttl_seconds=3600, secure_cookie=False
    )
    app = create_app(
        settings,
        RunRepository(settings.db_path),
        AppServices(
            authenticator=AccountAuthenticator(tmp_path / "accounts"),
            sessions=sessions,
        ),
    )
    return TestClient(app), sessions


def test_healthz_is_available_without_login(tmp_path: Path) -> None:
    client, _ = build_client(tmp_path)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_sets_signed_session_and_authenticates_root(tmp_path: Path) -> None:
    client, sessions = build_client(tmp_path)

    response = client.post(
        "/login",
        data={"username": "owen", "password": "password"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    cookie = response.cookies["project_creation_session"]
    assert sessions.verify(cookie) is not None
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["username"] == "owen"
    assert root.json()["role"] == "admin"
    assert root.json()["csrf_token"] == sessions.csrf_token(cookie)


def test_login_rejects_bad_password(tmp_path: Path) -> None:
    client, _ = build_client(tmp_path)

    response = client.post(
        "/login", data={"username": "owen", "password": "wrong"}
    )

    assert response.status_code == 401
    assert "project_creation_session" not in response.cookies


def test_existing_session_uses_current_account_status_and_role(tmp_path: Path) -> None:
    client, _ = build_client(tmp_path)
    client.post(
        "/login",
        data={"username": "owen", "password": "password"},
        follow_redirects=False,
    )
    user_id = account_store.list_users()[0]["id"]

    account_store.update_user(user_id, role="viewer")
    assert client.get("/").json()["role"] == "viewer"

    account_store.update_user(user_id, active=False)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_logout_requires_session_bound_csrf(tmp_path: Path) -> None:
    client, sessions = build_client(tmp_path)
    client.post(
        "/login",
        data={"username": "owen", "password": "password"},
        follow_redirects=False,
    )
    assert client.post("/logout", data={"csrf_token": "wrong"}).status_code == 403

    csrf_token = client.get("/").json()["csrf_token"]
    response = client.post(
        "/logout",
        data={"csrf_token": csrf_token},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
