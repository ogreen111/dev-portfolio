from collections.abc import Iterator

import pytest


@pytest.fixture(autouse=True)
def clear_external_credentials(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for name in (
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "CERT_PATH",
        "CERT_PASSWORD",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    yield
