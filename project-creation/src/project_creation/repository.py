"""SQLite operational state for resumable provisioning."""

from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

from project_creation.models import (
    GraphResource,
    ProvisioningManifest,
    ProvisioningRun,
    RunState,
    SiteTarget,
)


class StateConflict(RuntimeError):
    """Raised when a run changed after a caller read it."""


class RunNotFound(KeyError):
    """Raised when a run ID does not exist."""


class RunRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS provisioning_runs (
                    id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    current_revision INTEGER NOT NULL DEFAULT 0,
                    run_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS source_specs (
                    run_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_json TEXT NOT NULL,
                    PRIMARY KEY (run_id, source_id),
                    FOREIGN KEY (run_id) REFERENCES provisioning_runs(id)
                );
                CREATE TABLE IF NOT EXISTS detected_systems (
                    run_id TEXT NOT NULL,
                    system_id TEXT NOT NULL,
                    system_json TEXT NOT NULL,
                    PRIMARY KEY (run_id, system_id),
                    FOREIGN KEY (run_id) REFERENCES provisioning_runs(id)
                );
                CREATE TABLE IF NOT EXISTS detected_submittals (
                    run_id TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    record_json TEXT NOT NULL,
                    PRIMARY KEY (run_id, record_id),
                    FOREIGN KEY (run_id) REFERENCES provisioning_runs(id)
                );
                CREATE TABLE IF NOT EXISTS template_mappings (
                    run_id TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    mapping_json TEXT NOT NULL,
                    PRIMARY KEY (run_id, record_id),
                    FOREIGN KEY (run_id) REFERENCES provisioning_runs(id)
                );
                CREATE TABLE IF NOT EXISTS manifest_items (
                    run_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    item_id TEXT NOT NULL,
                    item_json TEXT NOT NULL,
                    PRIMARY KEY (run_id, revision, item_id),
                    FOREIGN KEY (run_id) REFERENCES provisioning_runs(id)
                );
                CREATE TABLE IF NOT EXISTS manifest_revisions (
                    run_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    manifest_hash TEXT NOT NULL,
                    manifest_json TEXT NOT NULL,
                    approved_by TEXT,
                    approved_at TEXT,
                    PRIMARY KEY (run_id, revision),
                    FOREIGN KEY (run_id) REFERENCES provisioning_runs(id)
                );
                CREATE TABLE IF NOT EXISTS graph_resources (
                    run_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    logical_id TEXT NOT NULL,
                    resource_json TEXT NOT NULL,
                    PRIMARY KEY (run_id, kind, logical_id),
                    FOREIGN KEY (run_id) REFERENCES provisioning_runs(id)
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES provisioning_runs(id)
                );
                """
            )

    def create_run(self, site: SiteTarget, actor: str) -> ProvisioningRun:
        now = datetime.now(UTC)
        run = ProvisioningRun(
            id=str(uuid.uuid4()),
            state=RunState.DRAFT,
            site=site,
            created_at=now,
            updated_at=now,
            initiated_by=actor,
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO provisioning_runs (id, state, current_revision, run_json)
                VALUES (?, ?, ?, ?)
                """,
                (run.id, run.state.value, run.current_revision, run.model_dump_json()),
            )
        return run

    def get_run(self, run_id: str) -> ProvisioningRun:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT run_json FROM provisioning_runs WHERE id = ?", (run_id,)
            ).fetchone()
        if row is None:
            raise RunNotFound(run_id)
        return ProvisioningRun.model_validate_json(row["run_json"])

    def transition(
        self, run_id: str, expected: RunState, target: RunState
    ) -> ProvisioningRun:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT state, run_json FROM provisioning_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
            if row is None:
                raise RunNotFound(run_id)
            if row["state"] != expected.value:
                raise StateConflict(
                    f"run {run_id} is not in expected state {expected.value}"
                )
            current = ProvisioningRun.model_validate_json(row["run_json"])
            updated = current.model_copy(
                update={"state": target, "updated_at": datetime.now(UTC)}
            )
            cursor = connection.execute(
                """
                UPDATE provisioning_runs
                SET state = ?, run_json = ?
                WHERE id = ? AND state = ?
                """,
                (target.value, updated.model_dump_json(), run_id, expected.value),
            )
            if cursor.rowcount != 1:
                raise StateConflict(
                    f"run {run_id} is not in expected state {expected.value}"
                )
        return updated

    def save_manifest_revision(self, manifest: ProvisioningManifest) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT current_revision, run_json FROM provisioning_runs WHERE id = ?",
                (manifest.run_id,),
            ).fetchone()
            if row is None:
                raise RunNotFound(manifest.run_id)
            expected_revision = int(row["current_revision"]) + 1
            if manifest.revision != expected_revision:
                raise StateConflict(
                    f"expected revision {expected_revision}, got {manifest.revision}"
                )
            run = ProvisioningRun.model_validate_json(row["run_json"])
            updated_run = run.model_copy(
                update={
                    "current_revision": manifest.revision,
                    "source_fingerprint": manifest.source_fingerprint,
                    "updated_at": datetime.now(UTC),
                }
            )
            connection.execute(
                """
                INSERT INTO manifest_revisions
                    (run_id, revision, manifest_hash, manifest_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    manifest.run_id,
                    manifest.revision,
                    manifest.manifest_hash,
                    manifest.model_dump_json(),
                ),
            )
            connection.executemany(
                """
                INSERT INTO manifest_items (run_id, revision, item_id, item_json)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        manifest.run_id,
                        manifest.revision,
                        item.id,
                        item.model_dump_json(),
                    )
                    for item in manifest.items
                ],
            )
            connection.execute(
                """
                UPDATE provisioning_runs
                SET current_revision = ?, run_json = ?
                WHERE id = ?
                """,
                (
                    manifest.revision,
                    updated_run.model_dump_json(),
                    manifest.run_id,
                ),
            )

    def list_manifest_revisions(self, run_id: str) -> list[ProvisioningManifest]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT manifest_json
                FROM manifest_revisions
                WHERE run_id = ?
                ORDER BY revision
                """,
                (run_id,),
            ).fetchall()
        return [
            ProvisioningManifest.model_validate_json(row["manifest_json"])
            for row in rows
        ]

    def save_graph_resource(self, run_id: str, resource: GraphResource) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO graph_resources (run_id, kind, logical_id, resource_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (run_id, kind, logical_id)
                DO UPDATE SET resource_json = excluded.resource_json
                """,
                (
                    run_id,
                    resource.kind.value,
                    resource.logical_id,
                    resource.model_dump_json(),
                ),
            )

    def list_graph_resources(self, run_id: str) -> list[GraphResource]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT resource_json
                FROM graph_resources
                WHERE run_id = ?
                ORDER BY rowid
                """,
                (run_id,),
            ).fetchall()
        return [GraphResource.model_validate_json(row["resource_json"]) for row in rows]
