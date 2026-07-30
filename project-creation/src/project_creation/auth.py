"""Local account authentication and signed browser sessions."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import threading
import time
from pathlib import Path
from typing import Literal

import account_store

from project_creation.models import LocalUser

Role = Literal["viewer", "reviewer", "admin"]
ROLE_RANK: dict[str, int] = {"viewer": 0, "reviewer": 1, "admin": 2}


def _encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode(encoded: str) -> bytes:
    padded = encoded + ("=" * (-len(encoded) % 4))
    return base64.urlsafe_b64decode(padded.encode("ascii"))


class AccountAuthenticator:
    _configuration_lock = threading.RLock()

    def __init__(self, state_dir: Path) -> None:
        self._state_dir = state_dir.expanduser()
        with self._configuration_lock:
            account_store.configure(state_dir=self._state_dir)

    def authenticate(self, username: str, password: str) -> LocalUser | None:
        with self._configuration_lock:
            account_store.configure(state_dir=self._state_dir)
            record = account_store.authenticate(username, password)
        return self._to_local_user(record)

    def current_user(self, user_id: str) -> LocalUser | None:
        with self._configuration_lock:
            account_store.configure(state_dir=self._state_dir)
            record = account_store.get_user_by_id(user_id)
        if record is not None and not record.get("active", True):
            return None
        return self._to_local_user(record)

    @staticmethod
    def _to_local_user(record: dict[str, object] | None) -> LocalUser | None:
        if record is None:
            return None
        return LocalUser(
            id=str(record["id"]),
            username=str(record["username"]),
            display_name=str(record["display_name"]),
            role=str(record["role"]),
        )


class SessionManager:
    def __init__(
        self,
        secret: str,
        *,
        ttl_seconds: int,
        secure_cookie: bool,
    ) -> None:
        if not secret:
            raise ValueError("session secret must be non-empty")
        if ttl_seconds <= 0:
            raise ValueError("session TTL must be positive")
        self._key = secret.encode("utf-8")
        self.ttl_seconds = ttl_seconds
        self.secure_cookie = secure_cookie

    @property
    def cookie_options(self) -> dict[str, bool | str | int]:
        return {
            "httponly": True,
            "samesite": "lax",
            "secure": self.secure_cookie,
            "max_age": self.ttl_seconds,
        }

    def issue(self, user: LocalUser, *, now: int | None = None) -> str:
        issued_at = int(time.time()) if now is None else now
        payload = {
            "user": user.model_dump(mode="json"),
            "iat": issued_at,
            "exp": issued_at + self.ttl_seconds,
            "nonce": secrets.token_urlsafe(12),
        }
        encoded_payload = _encode(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        signature = _encode(
            hmac.new(self._key, encoded_payload.encode("ascii"), hashlib.sha256).digest()
        )
        return f"{encoded_payload}.{signature}"

    def verify(self, cookie: str, *, now: int | None = None) -> LocalUser | None:
        try:
            encoded_payload, supplied_signature = cookie.split(".", 1)
            expected_signature = _encode(
                hmac.new(
                    self._key, encoded_payload.encode("ascii"), hashlib.sha256
                ).digest()
            )
            if not hmac.compare_digest(supplied_signature, expected_signature):
                return None
            payload = json.loads(_decode(encoded_payload))
            current_time = int(time.time()) if now is None else now
            if current_time >= int(payload["exp"]):
                return None
            return LocalUser.model_validate(payload["user"])
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return None

    def csrf_token(self, cookie: str) -> str:
        return _encode(
            hmac.new(
                self._key, f"csrf:{cookie}".encode("utf-8"), hashlib.sha256
            ).digest()
        )

    def verify_csrf(self, cookie: str, supplied_token: str) -> bool:
        if not cookie or not supplied_token:
            return False
        return hmac.compare_digest(self.csrf_token(cookie), supplied_token)


def has_required_role(user: LocalUser, required: Role) -> bool:
    return ROLE_RANK.get(user.role, -1) >= ROLE_RANK[required]
