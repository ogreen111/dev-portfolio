from datetime import UTC, datetime

from project_creation.models import ProvisioningRun, RunState, SiteTarget


def test_run_states_serialize_to_approved_values() -> None:
    assert [state.value for state in RunState] == [
        "draft",
        "analyzing",
        "needs_review",
        "ready",
        "provisioning",
        "partial_failure",
        "complete",
        "canceled",
    ]


def test_provisioning_run_round_trips_without_changing_identity() -> None:
    run = ProvisioningRun(
        id="run-123",
        state=RunState.DRAFT,
        site=SiteTarget(
            site_id="site-1",
            drive_id="drive-1",
            web_url="https://example.sharepoint.com/sites/project",
            display_name="Project",
        ),
        created_at=datetime(2026, 7, 29, tzinfo=UTC),
        updated_at=datetime(2026, 7, 29, tzinfo=UTC),
        initiated_by="owen",
    )

    restored = ProvisioningRun.model_validate_json(run.model_dump_json())

    assert restored == run
    assert restored.id == "run-123"
    assert restored.current_revision == 0
    assert restored.approved_manifest_hash is None
