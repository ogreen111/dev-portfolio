from pathlib import Path

import pytest

from project_creation.config import Settings


def test_settings_use_approved_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("PROJECT_CREATION_HOST", raising=False)
    monkeypatch.delenv("PROJECT_CREATION_PORT", raising=False)
    monkeypatch.delenv("PROJECT_CREATION_ALLOW_REMOTE", raising=False)
    monkeypatch.setenv("PROJECT_CREATION_DB", str(tmp_path / "state.db"))

    settings = Settings.from_env()

    assert settings.host == "127.0.0.1"
    assert settings.port == 8773
    assert settings.db_path == tmp_path / "state.db"
    assert settings.cyber_specs_path == "Proposals/Tech/Cyber/RFP Summary/Cyber Specs"
    assert settings.planner_template_id == "AHEqL4KIXU2P3AMIiuF3X4IAELH7"
    assert settings.default_owner == "ogreen@spectrumsi.com"


def test_settings_reject_remote_bind_without_opt_in(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PROJECT_CREATION_HOST", "0.0.0.0")
    monkeypatch.setenv("PROJECT_CREATION_ALLOW_REMOTE", "0")
    monkeypatch.setenv("PROJECT_CREATION_DB", str(tmp_path / "state.db"))

    with pytest.raises(ValueError, match="PROJECT_CREATION_ALLOW_REMOTE"):
        Settings.from_env()


def test_settings_allow_remote_bind_with_explicit_opt_in(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PROJECT_CREATION_HOST", "0.0.0.0")
    monkeypatch.setenv("PROJECT_CREATION_ALLOW_REMOTE", "true")
    monkeypatch.setenv("PROJECT_CREATION_DB", str(tmp_path / "state.db"))

    assert Settings.from_env().host == "0.0.0.0"


@pytest.mark.parametrize("host", ["127.0.0.2", "::1", "localhost."])
def test_settings_accept_all_loopback_bindings_without_remote_opt_in(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, host: str
) -> None:
    monkeypatch.setenv("PROJECT_CREATION_HOST", host)
    monkeypatch.setenv("PROJECT_CREATION_ALLOW_REMOTE", "0")
    monkeypatch.setenv("PROJECT_CREATION_DB", str(tmp_path / "state.db"))

    assert Settings.from_env().host == host


def test_settings_repr_redacts_session_secret(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PROJECT_CREATION_DB", str(tmp_path / "state.db"))
    monkeypatch.setenv("PROJECT_CREATION_SESSION_SECRET", "do-not-print-this")

    settings = Settings.from_env()

    assert "do-not-print-this" not in repr(settings)
