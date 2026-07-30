from pathlib import Path

import account_store

from project_creation.auth import (
    AccountAuthenticator,
    SessionManager,
    has_required_role,
)
from project_creation.models import LocalUser


def user(role: str = "reviewer") -> LocalUser:
    return LocalUser(
        id="user-1",
        username="owen",
        display_name="Owen",
        role=role,
    )


def test_account_authenticator_accepts_active_user_and_rejects_bad_password(
    tmp_path: Path,
) -> None:
    account_store.configure(state_dir=tmp_path)
    created = account_store.add_user(
        "owen", "correct-password", role="reviewer", display_name="Owen"
    )
    authenticator = AccountAuthenticator(tmp_path)

    authenticated = authenticator.authenticate("owen", "correct-password")

    assert authenticated == LocalUser(
        id=created["id"],
        username="owen",
        display_name="Owen",
        role="reviewer",
    )
    assert authenticator.authenticate("owen", "wrong-password") is None


def test_account_authenticator_rejects_inactive_user(tmp_path: Path) -> None:
    account_store.configure(state_dir=tmp_path)
    created = account_store.add_user("owen", "password", role="admin")
    account_store.update_user(created["id"], active=False)

    assert AccountAuthenticator(tmp_path).authenticate("owen", "password") is None


def test_account_authenticator_keeps_its_own_state_directory(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    account_store.configure(state_dir=first_dir)
    account_store.add_user("first-user", "first-password", role="reviewer")
    first = AccountAuthenticator(first_dir)

    account_store.configure(state_dir=second_dir)
    account_store.add_user("second-user", "second-password", role="reviewer")
    second = AccountAuthenticator(second_dir)

    assert first.authenticate("first-user", "first-password") is not None
    assert first.authenticate("second-user", "second-password") is None
    assert second.authenticate("second-user", "second-password") is not None


def test_signed_session_round_trip_and_expiry() -> None:
    manager = SessionManager("secret", ttl_seconds=60, secure_cookie=False)
    cookie = manager.issue(user(), now=1_000)

    assert manager.verify(cookie, now=1_059) == user()
    assert manager.verify(cookie, now=1_060) is None


def test_signed_session_rejects_tampering() -> None:
    manager = SessionManager("secret", ttl_seconds=60, secure_cookie=False)
    cookie = manager.issue(user(), now=1_000)
    replacement = "A" if cookie[-1] != "A" else "B"

    assert manager.verify(cookie[:-1] + replacement, now=1_001) is None


def test_csrf_token_is_bound_to_session_cookie() -> None:
    manager = SessionManager("secret", ttl_seconds=60, secure_cookie=False)
    first = manager.issue(user(), now=1_000)
    second = manager.issue(user(), now=1_001)

    assert manager.verify_csrf(first, manager.csrf_token(first))
    assert not manager.verify_csrf(first, manager.csrf_token(second))
    assert not manager.verify_csrf(first, "")


def test_cookie_options_are_http_only_lax_and_configurably_secure() -> None:
    insecure = SessionManager("secret", ttl_seconds=60, secure_cookie=False)
    secure = SessionManager("secret", ttl_seconds=60, secure_cookie=True)

    assert insecure.cookie_options == {
        "httponly": True,
        "samesite": "lax",
        "secure": False,
        "max_age": 60,
    }
    assert secure.cookie_options["secure"] is True


def test_role_ordering() -> None:
    assert has_required_role(user("admin"), "reviewer")
    assert has_required_role(user("reviewer"), "reviewer")
    assert not has_required_role(user("viewer"), "reviewer")
