import sqlite3
from pathlib import Path

import pytest

from project_creation.models import (
    GraphResource,
    ManifestItem,
    ProvisioningManifest,
    ResourceKind,
    RunState,
    SiteTarget,
)
from project_creation.repository import RunRepository, StateConflict


def site() -> SiteTarget:
    return SiteTarget(
        site_id="site-1",
        drive_id="drive-1",
        web_url="https://example.sharepoint.com/sites/project",
        display_name="Project",
    )


def manifest(run_id: str, revision: int, digest: str) -> ProvisioningManifest:
    return ProvisioningManifest(
        run_id=run_id,
        revision=revision,
        project_name="Project",
        site=site(),
        source_fingerprint=f"source-{revision}",
        buckets=("Planning/Backlog",),
        categories={"category1": "BACS"},
        items=(
            ManifestItem(
                id="item-1",
                record_id="record-1",
                system_name="BACS",
                submittal_name="Product Data",
                sd_code="SD-03",
                sd_title="Product Data",
                system_category="category1",
                sd_category="category2",
                destination_relative_path="06.Systems/BACS/Product Data",
            ),
        ),
        manifest_hash=digest,
    )


def test_repository_creates_all_core_tables(tmp_path: Path) -> None:
    RunRepository(tmp_path / "state.db")

    with sqlite3.connect(tmp_path / "state.db") as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {
        "provisioning_runs",
        "source_specs",
        "detected_systems",
        "detected_submittals",
        "template_mappings",
        "manifest_items",
        "manifest_revisions",
        "graph_resources",
        "audit_events",
    } <= tables


def test_create_and_transition_run_atomically(tmp_path: Path) -> None:
    repository = RunRepository(tmp_path / "state.db")
    run = repository.create_run(site(), actor="owen")

    transitioned = repository.transition(run.id, RunState.DRAFT, RunState.ANALYZING)

    assert transitioned.state is RunState.ANALYZING
    with pytest.raises(StateConflict):
        repository.transition(run.id, RunState.DRAFT, RunState.NEEDS_REVIEW)


def test_manifest_revisions_share_one_run_id(tmp_path: Path) -> None:
    repository = RunRepository(tmp_path / "state.db")
    run = repository.create_run(site(), actor="owen")

    repository.save_manifest_revision(manifest(run.id, 1, "hash-1"))
    repository.save_manifest_revision(manifest(run.id, 2, "hash-2"))

    revisions = repository.list_manifest_revisions(run.id)
    assert [(item.run_id, item.revision) for item in revisions] == [
        (run.id, 1),
        (run.id, 2),
    ]
    assert repository.get_run(run.id).current_revision == 2


def test_manifest_revision_must_be_next_in_sequence(tmp_path: Path) -> None:
    repository = RunRepository(tmp_path / "state.db")
    run = repository.create_run(site(), actor="owen")

    with pytest.raises(StateConflict, match="expected revision 1"):
        repository.save_manifest_revision(manifest(run.id, 2, "hash-2"))

    assert repository.get_run(run.id).current_revision == 0
    assert repository.list_manifest_revisions(run.id) == []


def test_graph_resource_is_persisted_immediately(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    repository = RunRepository(db_path)
    run = repository.create_run(site(), actor="owen")
    resource = GraphResource(
        kind=ResourceKind.PLAN,
        logical_id="project-plan",
        graph_id="plan-123",
        etag='"etag-1"',
    )

    repository.save_graph_resource(run.id, resource)

    reopened = RunRepository(db_path)
    assert reopened.list_graph_resources(run.id) == [resource]
