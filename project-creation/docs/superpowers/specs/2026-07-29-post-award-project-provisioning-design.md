# Post-Award Cyber Project Provisioning Design

**Date:** 2026-07-29
**Status:** Approved after written-spec review and Planner tenant spike
**Application:** `project-creation`
**Owner for initially provisioned Microsoft 365 Groups:** `ogreen@spectrumsi.com`

## 1. Purpose

Create a standalone internal application that provisions the cyber portion of a
newly awarded project after:

1. the award email and takeoff request have already been sent to Matt; and
2. IT has created the project SharePoint site.

The application starts with an existing SharePoint project site, reads the
awarded UFGS 25 05 11 specifications, previews the proposed project structure,
and—only after explicit user approval—creates:

- the standard post-award Cyber folder structure;
- one folder per detected system;
- one folder per required submittal within each system;
- the matched SSI Fileshare template contents inside each submittal folder;
- a new Microsoft 365 Group named exactly after the confirmed project name;
- a same-named Planner plan;
- the standard Planner bucket structure; and
- one unassigned Planner card per system/submittal combination.

This release does not automate the preceding award email, takeoff request,
personnel assignments, submittal submission, or government-approval workflow.

## 2. Confirmed User Decisions

- Build a new standalone `project-creation` web application.
- Use a preview-first workflow. No SharePoint or Planner resources are written
  before the final approval.
- Let users either paste a SharePoint site URL or choose from a list of recently
  created sites discovered through Microsoft Graph.
- Read specifications from:

  `Proposals/Tech/Cyber/RFP Summary/Cyber Specs`

- Propose the project name from the selected SharePoint site, but require the
  user to confirm or edit it.
- Use the exact confirmed project name for both the Microsoft 365 Group and
  Planner plan. Do not add a prefix or suffix.
- For the initial release, use `ogreen@spectrumsi.com` as the Group owner.
- For the initial release, add only that owner as a Group member. Adding other
  project stakeholders is a manual post-provisioning action, not card
  assignment and not part of this automation.
- Recreate the bucket structure from the Planner template plan:

  `AHEqL4KIXU2P3AMIiuF3X4IAELH7` (`Cyber Template`)

- Copy only the bucket structure. Do not copy the template plan's cards.
- Create all submittal cards unassigned in `Planning/Backlog`.
- Use the submittal name alone as the card title.
- Distinguish repeated submittal names with Planner labels:
  - one label for the system; and
  - one label for the SD category.
- Keep SD numbers as internal metadata. Do not include SD-number prefixes in
  SharePoint folder names or Planner card titles.
- Populate submittal folders with templates from the SSI Fileshare template
  library.
- Pause before provisioning when a required submittal cannot be matched
  confidently to a template.
- Use OpenAI as the default AI provider for non-CUI matching.
- Route CUI matching exclusively to the existing local Ollama model.
- Do not assign people to Planner cards during provisioning.

## 3. Reference Resources

### Planner template

Plan URL:

`https://planner.cloud.microsoft/webui/plan/AHEqL4KIXU2P3AMIiuF3X4IAELH7/view/board?tid=0a300250-5bb2-4fc4-9b86-6f58fcce0cd4`

The template defines these buckets:

1. `Complete`
2. `Pending Gov. Approval`
3. `Ready to Submit`
4. `In QC`
5. `Ready for QC`
6. `Executing`
7. `Planning/Backlog`
8. `Blocked`
9. `Resources`

The template's existing `Invoices`, `Folders`, and `Task 1 w/ Labels` cards are
not copied.

### Example project plan

Plan URL:

`https://planner.cloud.microsoft/webui/plan/Dw61G9TVEEu7lY4gOK2-m4IABxb7/view/board?tid=0a300250-5bb2-4fc4-9b86-6f58fcce0cd4`

The `RSA MSIC MACE` plan establishes the card convention:

- repeated titles are acceptable;
- the title is the submittal name only;
- a system label distinguishes the applicable system;
- a second label identifies the SD category;
- initial submittal cards are unassigned in `Planning/Backlog`.

### SSI Fileshare template library

Initial local reference path:

`SSI Fileshare - Documents/Integration and Cyber/Cyber/25.05.11-File Structure.Templates.Examples`

Production configuration must identify the corresponding SharePoint site,
drive, and library-relative path rather than depend on a user-specific local
mount.

## 4. User Workflow

1. The user signs in with the existing local SSI account system.
2. The start screen offers:
   - paste a SharePoint site URL; or
   - select a recently created accessible SharePoint site.
   Graph-powered recent-site discovery requires tenant-wide read permission
   such as `Sites.Read.All`; `Sites.Selected` alone does not support site
   search. A deployment using only `Sites.Selected` disables Graph discovery
   and offers pasted URL plus an optional IT-maintained known-site registry.
   In either deployment, IT must grant `Sites.Selected` write access to the
   chosen project site before it can be provisioned.
3. The application resolves the SharePoint site and document drive through
   Graph.
4. It validates that the Cyber Specs path exists and contains supported files.
5. It proposes a project name from the SharePoint site title.
6. The user must confirm or edit the project name.
7. The application reads all applicable UFGS 25 05 11 files.
8. It extracts systems, SD groups, submittal names, approval codes, and source
   citations.
9. It matches every required submittal to the SSI Fileshare template library.
10. If a system name or template match is uncertain, the run pauses before any
    writes and displays the resolution screen.
11. The application builds a final provisioning preview.
12. The user selects **Create Project**.
13. The application provisions the approved manifest.
14. The completion screen displays:
    - SharePoint Cyber-folder link;
    - Microsoft 365 Group link where available;
    - Planner plan link;
    - counts of systems, submittal folders, template files, and cards;
    - warnings or skipped items; and
    - a reminder that additional Planner users must be added to the private
      Microsoft 365 Group manually; and
    - audit/run identifier.

## 5. Preview Contract

The preview is the exact manifest the application will execute. It includes:

- selected SharePoint site, drive, and target Cyber folder;
- confirmed project and group name;
- default owner;
- source-specification file list and fingerprint;
- detected systems;
- normalized submittals and their internal SD metadata;
- output folders;
- source-to-destination template file mappings;
- template matches, confidence, reason, and approval source;
- Microsoft 365 Group properties;
- Planner plan title;
- bucket names and order;
- Planner label names;
- every proposed card title, system label, SD-category label, and bucket; and
- any warnings, conflicts, or user overrides.

No provisioning can begin while the manifest contains an unresolved item.

## 6. SharePoint Output

The application creates the standard structure under the existing project
`Cyber` folder:

```text
Cyber/
├── 01.Training & Regs/
├── 02.Submittal Register & SOVs/
├── 03.Cyber Summary/
├── 04.Precon Questionnaires/
├── 05.Drawings/
├── 06.Systems/
│   ├── <System Name>/
│   │   ├── <Submittal Name>/
│   │   │   └── <matched template contents>
│   │   └── ...
│   └── ...
├── 07.Post Award RFIs/
└── 08.Gov QC Review Doc/
```

Rules:

- System folder names come from the applicable 25 05 11 section title/system
  identity, normalized for SharePoint-invalid characters.
- Submittal folder names use only the normalized submittal name.
- SD numbers and group codes are stored in application metadata, not names.
- Standard folder contents are copied from the corresponding SSI Fileshare
  template directories.
- Each submittal folder receives the recursively enumerated contents of its
  approved template folder.
- Historical `Examples` directories are included only when they are part of the
  approved source template manifest. The preview makes their inclusion
  explicit.
- The application does not overwrite a different existing file silently.

Because the template library and project site can be in different SharePoint
drives/site collections, the implementation must support download-from-source
and upload-to-destination. It must not assume that Graph's asynchronous
`driveItem/copy` operation supports the required cross-site copy.

## 7. Specification Analysis

The analyzer reuses the proven parsing and normalized submittal extraction logic
from `rfp-automation` rather than creating a second interpretation of UFGS
25 05 11.

Supported input for the first release:

- PDF;
- DOCX; and
- OCR fallback for image-only PDFs when the existing parser supports it.

For each result, the analyzer returns:

- source file;
- source section;
- system name;
- SD group code;
- SD group title;
- normalized submittal name;
- approval code when present; and
- source citation or page/section reference.

One logical card/folder record is created per unique
`system + SD group + normalized submittal name`. Exact duplicates within the
same system are collapsed while preserving all source citations.

If the analyzer cannot identify a system reliably, the preview pauses and asks
the user to name or merge the system before template matching proceeds.

## 8. Template Matching

Template matching uses a layered, explainable process:

1. **Approved mapping**
   - Look up a previously approved normalized submittal-to-template mapping.
2. **Deterministic normalization**
   - Normalize punctuation, whitespace, plurals, common abbreviations, and
     approved aliases.
3. **Candidate scoring**
   - Rank candidate template folders using token and phrase similarity.
4. **AI assistance**
   - Invoke AI only when the preceding stages do not produce a confident,
     unambiguous match.
5. **Human approval**
   - Every AI-assisted match must be approved or changed before provisioning.

The AI request contains only:

- extracted submittal name;
- SD group code and title;
- system name;
- candidate template folder names; and
- deterministic similarity scores.

The AI response follows a structured schema:

```json
{
  "selected_template": "string or null",
  "confidence": 0.0,
  "reason": "short explanation",
  "needs_human_review": true
}
```

The model does not receive the complete specification for this task.

### Provider routing

- Default non-CUI provider: OpenAI.
- Optional configured non-CUI providers: Anthropic or local Ollama.
- CUI-marked source: local Ollama only.
- CUI classification is evaluated at the source-file and extracted-record
  levels. Every submittal record inherits the most restrictive classification
  of its source file and cited source section. A record derived from any
  CUI-marked source is CUI even when the extracted name itself is unmarked.
- If the local model is unavailable for a CUI run, the workflow pauses for
  manual resolution.
- CUI content is never sent to OpenAI or Anthropic.

The application reuses `rfp-automation` CUI detection and local-model
configuration patterns. AI prompts and specification text are not written to
the audit database. The audit record includes provider, model, timing,
confidence, and outcome without sensitive content.

### Unmatched-template choices

For each unresolved submittal, the user may:

- select the correct SSI Fileshare template;
- explicitly create an empty submittal folder;
- exclude the extracted submittal from this provisioning run; or
- cancel the run.

Approved selections may be saved as aliases for future projects. Empty-folder
and exclusion decisions are project-specific and are not promoted to global
aliases automatically.

## 9. Microsoft 365 Group and Planner Provisioning

### Group

- Display name: exact confirmed project name.
- Mail nickname: deterministic sanitized form of the confirmed name, with a
  collision check before writes.
- Both display-name and mail-nickname conflicts pause the run before writes.
- Type: Microsoft 365 unified group.
- Visibility: configured deployment default; initial recommendation is
  `Private`.
- Owner: configured initial owner for `ogreen@spectrumsi.com`.
- Member: add the configured owner as a member so the plan is immediately
  accessible.

The owner is configured, not hardcoded:

```text
PROJECT_CREATION_DEFAULT_OWNER=ogreen@spectrumsi.com
PROJECT_CREATION_DEFAULT_OWNER_ID=<Entra object ID, optional>
```

If the object ID is configured, the application does not need to resolve the
owner by email on every run.

Microsoft 365 Group creation is eventually consistent. After Graph returns
`201`, the orchestrator uses bounded condition polling to verify that the Group,
owner, and member bindings are readable before it creates the Planner plan.
Transient `404` responses during this readiness window are retried; exhaustion
becomes a resumable partial failure.

Creating the Microsoft 365 Group also creates a group-connected SharePoint site.
That site is not the document destination. The IT-created project SharePoint
site remains the authoritative destination for the Cyber folders.

### Plan

- Plan title: exact confirmed project name.
- Container: newly created Microsoft 365 Group.
- Template behavior: recreate the template definition; do not copy template
  tasks.

The application recreates the nine approved buckets in template order.

### Labels

The application creates plan category descriptions for:

- every detected system; and
- every SD category used by at least one extracted submittal.

Planner supports a bounded category set. If the union of system and SD-category
labels exceeds the supported capacity, the run pauses before writes and asks
the user to consolidate label names.

### Cards

One Planner card is created per manifest system/submittal record:

- title: normalized submittal name only;
- bucket: `Planning/Backlog`;
- assignment: none;
- system label: detected system;
- SD-category label: normalized SD group title;
- percent complete: `0`;
- internal provisioning metadata: Graph task ID and source record ID.

The application also creates a generated `Folders` card in `Resources` with a
link to the authoritative SharePoint Cyber folder. This card is generated from
the new project's data; it is not copied from the template plan.

### Provisioning order

The orchestrator executes the approved manifest in this dependency order:

1. create and populate the SharePoint folders;
2. create the Microsoft 365 Group and bind its owner/member;
3. create the Planner plan in that Group;
4. recreate the buckets in template order;
5. configure the plan category descriptions;
6. create the unassigned submittal cards;
7. update task details and references; and
8. create the `Folders` resource card after its authoritative SharePoint link
   is known.

Each successful step persists its Graph resource IDs and ETags before the next
step begins. Resume starts at the first incomplete step after reconciling all
previously persisted resources.

## 10. Authentication and Authorization

### Initial application authentication

- Reuse the portfolio `account-store` local account system.
- Roles:
  - `admin`: configure integrations and provision projects;
  - `reviewer`: prepare, approve, and provision projects;
  - `viewer`: inspect previews and completed runs only.
- Microsoft/Entra interactive sign-in is a future enhancement.

### Microsoft Graph authentication

Use the existing certificate-based service-principal pattern from
`rfp-automation`.

Expected Graph capabilities include:

- discover and read SharePoint sites/drives;
- read specification and template files;
- write folders and template files to the selected project site;
- resolve the configured owner when an owner object ID is not configured;
- create Microsoft 365 Groups and membership/ownership references;
- create Planner plans, buckets, plan details/categories, tasks, and task
  details; and
- read created resources for reconciliation.

The application performs a read-only permission preflight before enabling
**Create Project**. At minimum, deployment must account for:

- `Tasks.ReadWrite.All`;
- Group creation/write permissions appropriate to the tenant;
- `User.Read.All` if resolving `ogreen@spectrumsi.com` dynamically;
- `Sites.Read.All` if Graph-powered recent-site discovery is enabled;
- read access to the SSI Fileshare template site;
- read access to the selected project site; and
- IT/operator attestation that the selected project's `Sites.Selected` grant
  includes `write`.

If `Sites.Selected` is used for least privilege, IT must grant the application
write access to each newly created project site as part of the site-creation
handoff and before the user starts project provisioning. Merely creating the
site does not grant the application read or write access, and a
`Sites.Selected` grant does not make the site searchable through Graph. The app
surfaces a completely missing site grant as a pasted-site/known-site preflight
failure.

The read-only preflight cannot distinguish a site-specific `read` grant from a
site-specific `write` grant without broader permission to enumerate site
permissions. The application does not request `Sites.FullControl.All` for this
check. Instead, the approval records the IT/operator attestation, and the first
audited SharePoint folder creation after approval verifies actual write
capability. A `403` stops the run before any Group or Planner resource is
created, records a permission failure, and offers resume after IT corrects the
grant.

## 11. Provisioning State and Idempotency

The application uses SQLite for operational state. It does not store
specification contents.

Core records:

- `provisioning_runs`;
- `source_specs`;
- `detected_systems`;
- `detected_submittals`;
- `template_mappings`;
- `manifest_items`;
- `graph_resources`; and
- `audit_events`.

Each run records:

- immutable run ID;
- selected site and drive IDs;
- target folder ID;
- confirmed project name;
- source-spec fingerprint;
- manifest hash;
- current state;
- created Graph resource IDs;
- timestamps; and
- initiating local user.

Run states:

- `draft`;
- `analyzing`;
- `needs_review`;
- `ready`;
- `provisioning`;
- `partial_failure`;
- `complete`; and
- `canceled`.

Idempotency rules:

- Graph IDs are persisted immediately after successful creation.
- Resume reconciles persisted IDs with live Graph state before issuing writes.
- Existing matching folders and files are reused.
- Existing same-name files are compared with SHA-256 content hashes. A matching
  hash reuses the file; a different hash causes a review pause. Modified dates
  and file sizes are not sufficient identity checks.
- Cards are reconciled using the run's stable manifest item IDs and persisted
  task IDs, not title alone.
- The application never auto-deletes a partially created Microsoft 365 Group,
  plan, folder, or file.
- Re-running analysis after the source-spec fingerprint changes creates a new
  manifest revision within the same immutable provisioning run ID and requires
  approval again. All revisions share the run's persisted Graph resource IDs,
  so reconciliation spans revisions and cannot recreate an already-provisioned
  folder, Group, plan, bucket, or task.

## 12. Failure and Conflict Handling

The application pauses before writes for:

- missing or inaccessible Cyber Specs path;
- no applicable 25 05 11 content;
- ambiguous system identity;
- missing or ambiguous template match;
- duplicate normalized system names;
- group display-name or mail-nickname conflict;
- Planner label-capacity overflow;
- target file conflict;
- missing Graph write permission; or
- source specifications changing after preview.

For a mid-provisioning failure:

- preserve successfully created resource IDs;
- record the failed operation and Graph response metadata;
- show completed, pending, and failed items;
- provide **Resume Provisioning**; and
- reconcile before retrying.

Automatic destructive rollback is out of scope.

Planner updates and deletes that require optimistic concurrency use the current
resource `@odata.etag` in `If-Match`. This applies to plan-details,
task-details, task updates, and bucket updates/deletes—not resource-creation
POSTs, which have no existing ETag. The client treats `409` or `412` as a
reconciliation pause rather than blindly retrying with stale state.

## 13. Audit and Sensitive-Data Handling

Audit events include:

- actor;
- timestamp;
- run ID;
- action;
- target resource type and ID;
- Graph endpoint class and status;
- duration;
- before/after identifiers when applicable;
- AI provider/model and confidence metadata; and
- user override reason.

Audit records exclude:

- access tokens;
- certificate/private-key material;
- API keys;
- complete specification text;
- AI prompt bodies;
- file contents; and
- CUI excerpts.

Every Graph write passes through one audited client wrapper. File names and
resource links are retained because they are required for provisioning
traceability and operator support.

## 14. Application Boundaries

Recommended stack:

- Python 3.12;
- FastAPI;
- server-rendered HTML with minimal JavaScript;
- SQLite;
- `account-store`;
- Microsoft Graph REST calls using the existing certificate-auth pattern;
- parsing/submittal modules reused from `rfp-automation`;
- OpenAI default provider for non-CUI matching;
- optional Anthropic provider;
- existing Ollama `gpt-oss:120b` local provider for CUI; and
- pytest with fake Graph and model clients.

Focused components:

- `auth`: local application sessions and roles;
- `graph_auth`: certificate token acquisition;
- `sharepoint`: site discovery, path resolution, listing, download, folder
  creation, upload, and reconciliation;
- `spec_analysis`: adapter around `rfp-automation` parsing/extraction;
- `template_catalog`: recursive template inventory and normalized aliases;
- `template_matcher`: deterministic and AI-assisted matching;
- `manifest`: preview construction, hashing, and validation;
- `planner`: Group/plan/bucket/label/task provisioning;
- `provisioning`: resumable orchestration; and
- `audit`: metadata-only audit logging.

These components communicate through typed records and injected clients so
tests never require live Graph or AI access.

## 15. Testing Strategy

All automated tests are hermetic.

### Unit tests

- SharePoint URL and site-ID parsing;
- project-name proposal and validation;
- folder-name sanitization;
- system and submittal deduplication;
- template normalization and alias matching;
- AI structured-response validation;
- CUI provider routing;
- manifest hashing;
- mail-nickname generation and collision handling;
- Planner category assignment and capacity validation;
- card payload generation; and
- state transitions/idempotency keys.

### Integration tests with fakes

- pasted-site workflow;
- discovered-site workflow;
- multiple 25 05 11 systems;
- repeated submittal names across systems;
- unmatched template review and resume;
- CUI run with healthy local model;
- CUI run with unavailable local model;
- complete SharePoint + Group + Planner provisioning;
- file conflict before writes;
- Graph failure after partial creation;
- resume without duplicates;
- changed specifications invalidating an approved manifest; and
- permission preflight failure.

### Contract tests

Record sanitized Graph response shapes for:

- site resolution;
- drive/folder listing;
- small-file download/upload;
- Group creation;
- owner/member binding;
- Planner plan creation;
- bucket creation;
- plan details/category update;
- task creation; and
- task-details reference update.

The Planner contract suite covers application-only access and required
optimistic-concurrency behavior, including `If-Match`, ETag refresh, and
controlled handling of `409`/`412` responses.

Live smoke tests must use a dedicated sandbox site and sandbox Group/plan, run
only through an explicit operator command, and default to dry-run.

Before implementation begins, a one-time live tenant spike must prove that the
existing certificate-based service principal can perform this complete Planner
round trip:

1. create a private temporary Microsoft 365 Group;
2. add `ogreen@spectrumsi.com` as owner and member;
3. create a plan in that Group;
4. create a bucket;
5. update plan category descriptions with `If-Match`;
6. create an unassigned task with an applied category;
7. update task details with `If-Match`; and
8. read back and verify the created resources.

The spike records status codes and resource IDs without tokens or response
content. After Group creation, a `finally` cleanup path attempts to soft-delete
the temporary Group on both success and failure; Microsoft 365 soft deletion
keeps the Group recoverable during the tenant retention window. Cleanup failure
is reported with the temporary Group ID and requires manual deletion before a
retry. Any failed capability operation blocks implementation until the
permission or API contract is corrected and the spike passes.

### Tenant-spike evidence

The prerequisite spike passed on 2026-07-29 using the existing
`SSI-RFP-Automation` certificate-based service principal:

| Operation | Result |
|---|---:|
| Resolve `ogreen@spectrumsi.com` | `200` |
| Create temporary private Microsoft 365 Group | `201` |
| Read back owner/member bindings | eventual `200`; both verified |
| Create Planner plan | `201` |
| Create `Planning/Backlog` bucket | `201` |
| Read plan details and ETag | `200` |
| Update plan category descriptions with `If-Match` | `204` |
| Create unassigned categorized task | `201` |
| Read task details and ETag | `200` |
| Update task details with `If-Match` | `204` |
| Read back plan, buckets, tasks, categories, and task details | all `200` |
| Soft-delete temporary Group and contained test resources | `204` |

Read-back verification confirmed the exact plan title, bucket ID, task ID,
category description, task-details update, and empty assignments. The temporary
resources were:

- Group: `009d4e5b-a486-406a-bb33-6dc84d6916e7`;
- Plan: `YyRswa_RIE62Rym4SaK7CIIAF5dt`;
- Bucket: `s5DjP1rPO0-y5unNmykooYIADcG2`; and
- Task: `yTRmG0lRQEWTd1PGbrWm6oIAGIfL`.

This result resolves the written-spec review concern about application-only
Planner writes for the initial tenant and credential configuration. Contract
tests and the explicit live sandbox smoke command remain required so future
permission or Graph behavior changes fail closed.

## 16. Configuration

Representative configuration:

```text
PROJECT_CREATION_HOST=127.0.0.1
PROJECT_CREATION_PORT=<portfolio-assigned port>
PROJECT_CREATION_DB=<local state path>

AZURE_TENANT_ID=<tenant>
AZURE_CLIENT_ID=<application>
CERT_PATH=<certificate path>
CERT_PASSWORD=<secret>

PROJECT_CREATION_DEFAULT_OWNER=ogreen@spectrumsi.com
PROJECT_CREATION_DEFAULT_OWNER_ID=<optional object ID>
PROJECT_CREATION_PLANNER_TEMPLATE_ID=AHEqL4KIXU2P3AMIiuF3X4IAELH7
PROJECT_CREATION_CYBER_SPECS_PATH=Proposals/Tech/Cyber/RFP Summary/Cyber Specs

PROJECT_CREATION_TEMPLATE_SITE_URL=<SSI Fileshare site>
PROJECT_CREATION_TEMPLATE_LIBRARY=<document library>
PROJECT_CREATION_TEMPLATE_PATH=Integration and Cyber/Cyber/25.05.11-File Structure.Templates.Examples

PROJECT_CREATION_LLM_PROVIDER=openai
OPENAI_API_KEY=<secret>
PROJECT_CREATION_OPENAI_MODEL=<configured supported model>
PROJECT_CREATION_LOCAL_LLM_URL=http://127.0.0.1:11434
PROJECT_CREATION_LOCAL_LLM_MODEL=gpt-oss:120b
```

Secrets must be supplied through environment/deployment configuration and must
not be stored in SQLite or committed.

## 17. Done Criteria

The first release is done when an authorized user can:

1. select or paste a valid IT-created project SharePoint site;
2. verify the exact project name;
3. analyze the SharePoint Cyber Specs folder;
4. review detected systems and submittals;
5. resolve every uncertain template match, including AI suggestions;
6. preview the complete immutable provisioning manifest;
7. create the approved standard folders and populated submittal folders;
8. create the same-named Microsoft 365 Group owned by
   `ogreen@spectrumsi.com`;
9. create the same-named Planner plan and nine approved buckets;
10. create unassigned submittal cards in `Planning/Backlog` with system and
    SD-category labels;
11. create the generated `Folders` resource card;
12. recover from an injected mid-run failure without duplicate resources; and
13. inspect a complete metadata-only audit history.

## 18. Explicitly Out of Scope

- Sending the award email or takeoff request to Matt.
- Creating the IT-managed project SharePoint site.
- Assigning Planner cards.
- Copying template Planner cards.
- Updating the SOV or Submittal Register.
- Submittal QC, PDF conversion, DoD SAFE delivery, or approval processing.
- Automatic rollback or deletion of partially created cloud resources.
- Microsoft/Entra interactive login in the initial release.
- Using the Microsoft 365 Group's generated SharePoint site as the project
  document repository.
