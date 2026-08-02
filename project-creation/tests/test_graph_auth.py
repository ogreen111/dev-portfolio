import base64
import json

import pytest

from project_creation.graph_auth import (
    CertificateTokenProvider,
    require_application_roles,
)


def jwt_with_roles(*roles: str) -> str:
    payload = base64.urlsafe_b64encode(
        json.dumps({"roles": list(roles)}).encode()
    ).decode().rstrip("=")
    return f"header.{payload}.signature"


def test_certificate_provider_loads_auth_lazily_and_delegates_token_caching() -> None:
    calls: list[str] = []

    class Auth:
        def get_access_token(self) -> str:
            calls.append("token")
            return "secret-token"

    def loader() -> Auth:
        calls.append("load")
        return Auth()

    provider = CertificateTokenProvider(loader=loader)
    assert calls == []

    assert provider.get_token() == "secret-token"
    assert provider.get_token() == "secret-token"
    assert calls == ["load", "token", "token"]


def test_required_application_roles_include_discovery_only_when_enabled() -> None:
    token = jwt_with_roles(
        "Tasks.ReadWrite.All",
        "Group.ReadWrite.All",
        "Sites.Selected",
    )

    assert require_application_roles(token, discovery_enabled=False) == frozenset(
        {"Tasks.ReadWrite.All", "Group.ReadWrite.All", "Sites.Selected"}
    )
    with pytest.raises(PermissionError, match="Sites.Read.All"):
        require_application_roles(token, discovery_enabled=True)


def test_required_application_roles_reject_delegated_or_incomplete_token() -> None:
    with pytest.raises(PermissionError, match="Tasks.ReadWrite.All"):
        require_application_roles(jwt_with_roles("Group.ReadWrite.All"))

    with pytest.raises(PermissionError, match="inspect"):
        require_application_roles("header.%%%%.signature")

    read_only = jwt_with_roles(
        "Tasks.ReadWrite.All", "Group.ReadWrite.All", "Sites.Read.All"
    )
    with pytest.raises(PermissionError, match="site-write"):
        require_application_roles(read_only, discovery_enabled=True)


def test_broader_site_write_role_supports_discovery() -> None:
    token = jwt_with_roles(
        "Tasks.ReadWrite.All",
        "Group.ReadWrite.All",
        "Sites.ReadWrite.All",
    )
    assert "Sites.ReadWrite.All" in require_application_roles(
        token, discovery_enabled=True
    )
