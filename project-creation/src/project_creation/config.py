"""Environment-backed application configuration."""

from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

DEFAULT_CYBER_SPECS_PATH = "Proposals/Tech/Cyber/RFP Summary/Cyber Specs"
DEFAULT_PLANNER_TEMPLATE_ID = "AHEqL4KIXU2P3AMIiuF3X4IAELH7"
DEFAULT_OWNER = "ogreen@spectrumsi.com"
def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def _is_loopback_host(host: str) -> bool:
    if host.rstrip(".").lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int
    allow_remote: bool
    db_path: Path
    cyber_specs_path: str
    planner_template_id: str
    default_owner: str
    session_secret: str = field(repr=False)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        source = os.environ if env is None else env
        host = source.get("PROJECT_CREATION_HOST", "127.0.0.1").strip()
        allow_remote = _parse_bool(source.get("PROJECT_CREATION_ALLOW_REMOTE"))
        if not _is_loopback_host(host) and not allow_remote:
            raise ValueError(
                "non-loopback binding requires PROJECT_CREATION_ALLOW_REMOTE=1"
            )

        port = int(source.get("PROJECT_CREATION_PORT", "8773"))
        if not 1 <= port <= 65535:
            raise ValueError("PROJECT_CREATION_PORT must be between 1 and 65535")

        return cls(
            host=host,
            port=port,
            allow_remote=allow_remote,
            db_path=Path(source.get("PROJECT_CREATION_DB", "project-creation.db")).expanduser(),
            cyber_specs_path=source.get(
                "PROJECT_CREATION_CYBER_SPECS_PATH", DEFAULT_CYBER_SPECS_PATH
            ).strip(),
            planner_template_id=source.get(
                "PROJECT_CREATION_PLANNER_TEMPLATE_ID", DEFAULT_PLANNER_TEMPLATE_ID
            ).strip(),
            default_owner=source.get(
                "PROJECT_CREATION_DEFAULT_OWNER", DEFAULT_OWNER
            ).strip(),
            session_secret=source.get("PROJECT_CREATION_SESSION_SECRET", ""),
        )
