"""Narrow adapters around the proven rfp-automation Graph authentication."""

from __future__ import annotations

import base64
import binascii
import json
from collections.abc import Callable
from typing import Protocol

from rfp_automation.graph_auth import load_auth_from_env


class GraphAuthLike(Protocol):
    def get_access_token(self) -> str: ...


class CertificateTokenProvider:
    """Load certificate auth lazily while leaving token caching to GraphAuth."""

    def __init__(
        self,
        *,
        loader: Callable[[], GraphAuthLike] = load_auth_from_env,
    ) -> None:
        self._loader = loader
        self._auth: GraphAuthLike | None = None

    def get_token(self) -> str:
        if self._auth is None:
            self._auth = self._loader()
        return self._auth.get_access_token()


def _application_roles(token: str) -> frozenset[str]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("token is not a JWT")
        encoded = parts[1] + ("=" * (-len(parts[1]) % 4))
        payload = json.loads(base64.urlsafe_b64decode(encoded))
        roles = payload.get("roles", [])
        if not isinstance(roles, list):
            raise ValueError("roles claim is not a list")
        return frozenset(str(role) for role in roles)
    except (
        ValueError,
        TypeError,
        UnicodeDecodeError,
        binascii.Error,
        json.JSONDecodeError,
    ) as exc:
        raise PermissionError("unable to inspect Graph application roles") from exc


def require_application_roles(
    token: str,
    *,
    discovery_enabled: bool = False,
) -> frozenset[str]:
    roles = _application_roles(token)
    required = {"Tasks.ReadWrite.All", "Group.ReadWrite.All"}
    missing = required - roles
    if missing:
        raise PermissionError(
            "missing Graph application roles: " + ", ".join(sorted(missing))
        )
    site_write_roles = {"Sites.Selected", "Sites.ReadWrite.All", "Sites.FullControl.All"}
    if not (site_write_roles & roles):
        raise PermissionError(
            "missing Graph site-write application role: Sites.Selected, "
            "Sites.ReadWrite.All, or Sites.FullControl.All"
        )
    discovery_roles = {"Sites.Read.All", "Sites.ReadWrite.All", "Sites.FullControl.All"}
    if discovery_enabled and not (discovery_roles & roles):
        raise PermissionError("missing Graph application role: Sites.Read.All")
    return roles
