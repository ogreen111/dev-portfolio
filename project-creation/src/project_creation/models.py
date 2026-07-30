"""Typed records shared across analysis, review, and provisioning."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class RunState(StrEnum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    NEEDS_REVIEW = "needs_review"
    READY = "ready"
    PROVISIONING = "provisioning"
    PARTIAL_FAILURE = "partial_failure"
    COMPLETE = "complete"
    CANCELED = "canceled"


class MappingChoice(StrEnum):
    TEMPLATE = "template"
    EMPTY_FOLDER = "empty_folder"
    EXCLUDE = "exclude"
    CANCEL = "cancel"


class MatchMethod(StrEnum):
    EXACT = "exact"
    ALIAS = "alias"
    CONTAINMENT = "containment"
    SIMILARITY = "similarity"
    AI = "ai"
    HUMAN = "human"


class ResourceKind(StrEnum):
    FOLDER = "folder"
    FILE = "file"
    GROUP = "group"
    PLAN = "plan"
    BUCKET = "bucket"
    TASK = "task"


class SiteTarget(FrozenModel):
    site_id: str
    drive_id: str
    web_url: str
    display_name: str


class SourceSpec(FrozenModel):
    id: str
    drive_item_id: str
    name: str
    sha256: str
    cui: bool
    size: int | None = None


class DetectedSystem(FrozenModel):
    id: str
    name: str
    source_spec_ids: tuple[str, ...] = ()


class SubmittalRecord(FrozenModel):
    id: str
    system_id: str
    system_name: str
    sd_code: str
    sd_title: str
    name: str
    approval_code: str | None
    source_spec_id: str
    source_citation: str
    cui: bool


class TemplateEntry(FrozenModel):
    id: str
    drive_item_id: str
    relative_path: str
    normalized_name: str
    aliases: tuple[str, ...] = ()


class TemplateMapping(FrozenModel):
    record_id: str
    choice: MappingChoice
    template_id: str | None = None
    method: MatchMethod
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    approved_by: str | None = None


class ManifestItem(FrozenModel):
    id: str
    record_id: str
    system_name: str
    submittal_name: str
    sd_code: str
    sd_title: str
    system_category: str
    sd_category: str
    destination_relative_path: str
    source_template_ids: tuple[str, ...] = ()


class ProvisioningManifest(FrozenModel):
    run_id: str
    revision: int
    project_name: str
    site: SiteTarget
    source_fingerprint: str
    buckets: tuple[str, ...]
    categories: dict[str, str]
    items: tuple[ManifestItem, ...]
    manifest_hash: str


class GraphResource(FrozenModel):
    kind: ResourceKind
    logical_id: str
    graph_id: str
    parent_graph_id: str | None = None
    etag: str | None = None
    web_url: str | None = None


class AuditEvent(FrozenModel):
    id: str
    run_id: str
    actor: str
    source: str
    action: str
    timestamp: datetime
    resource_kind: ResourceKind | None = None
    resource_id: str | None = None
    endpoint_class: str | None = None
    status: int | None = None
    duration_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LocalUser(FrozenModel):
    id: str
    username: str
    display_name: str
    role: str


class ProvisioningRun(FrozenModel):
    id: str
    state: RunState
    site: SiteTarget
    created_at: datetime
    updated_at: datetime
    initiated_by: str
    confirmed_project_name: str | None = None
    source_fingerprint: str | None = None
    current_revision: int = 0
    approved_manifest_hash: str | None = None
    failure_operation: str | None = None
    failure_message: str | None = None
