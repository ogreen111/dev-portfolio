# Dev Portfolio — Codex Context

This is the `dev-portfolio` git repo, checked out in two places on this
Mac: `~/dev/` (primary, non-iCloud-synced — the destination for the
project relocations below) and `~/Documents/dev/` (the original
iCloud-synced workspace every project in the registry below that needed
relocating has now been moved out of — see the "lives outside this tree"
notes below for the full history; a few registry entries, like `scripts`,
`deploy`, and vendored third-party code, were never part of
`~/Documents/dev`'s own tracked history and needed no relocation). The
registry below mirrors the full 31-project portfolio, organized around
three core domains:

1. **DoD/MILCON cybersecurity proposal automation** — RFP intake → pricing → tech proposal → EAC tracking
2. **BAS/OT network engineering** — passive discovery, BACnet simulation, site scanning, hardware prototypes
3. **SSi internal productivity** — email triage, project financial tracking, past-performance management

---

## Project Registry

| Project | Purpose | Status |
|---|---|---|
| rfp-automation | DoD RFP intake, scope extraction, proposal drafting | Production |
| cyber-artifact-gen | BAS→diagram/schematic conversion for proposals | Utility |
| email-processor | Inbound RFI/RFQ/RFP email triage and summarization | Production |
| outlook-followup | "Follow-Up Reminder" Office.js add-in (~1,300 LOC): intended to flag sent mail and remind on no-reply via Outlook flag + To Do task + taskpane dashboard, with Graph reply detection and `roamingSettings` sync. **Graph-backed half is non-functional** — `mailbox.js` passes a callback to the promise-only `Office.auth.getAccessToken`, so `getGraphToken()` never settles; and `storage.addItem()` dedups on `conversationId`, which is `null` at compose time for a brand-new (non-reply) message — replies inherit a real `conversationId` from the thread — so `OnMessageSend` auto-tracking on consecutive new messages overwrites the previous entry | Written, never run — not a stub, but not working either |
| past-performance | SSi past-performance doc search + extraction | v1 |
| project-tracking | Job budget/cost/labor/submittal dashboard; React v2 UI primary, Planner/SharePoint Graph sync | v1 |
| project-monitor | Project folder + Outlook email → PM status via entity registers (contracts, mods, POs, invoices, pay apps) | v2 |
| cyber-brain | SSi cyber group knowledge system: Graph ingestion (SharePoint/Planner/Teams/email) → per-project event stream, briefs, cited Q&A | v0.1 |
| daily-summary | Power Automate daily email digest solution | v0 |
| fulcrum-replacement | Offline-first mobile field data collection platform (Fulcrum SaaS replacement) | Design only |
| network-scanner | Active network discovery + BACnet enumeration | v1 |
| ethernet-link-analyzer | Passive LLDP/CDP Ethernet discovery; Pi field appliance w/ touch UI, battery, gated active tests | Phase 4 |
| virtual-devices | BACnet/IP virtual building fleet (76 devices) | v1 |
| digital-twin | DOPPEL — FRCS HVAC plant digital twin + fault injection; selectable twin models (office-building / barracks-cep campus, mutually exclusive, live-switchable from the HMI), electrical model, 65-detector FDD on office-building after the open-fdd parity port (barracks-cep coverage partial) + cross-scope cascade diagnosis; config-driven mode emulates a real site from a Niagara Supervisor backup (via niagara-config, designed-for future third model) — incl. per-detector role catalog + `config coverage` report, fault injection addressed by real equipment id, findings in real config names, `config export-fixtures` labeled diagnosis fixtures, and backup **history replay** (`HistoryReplaySource`, live via `TWIN_HISTORY_REPLAY` or headless via `config replay-backup`) | rev 2.15 |
| pocket-probe | STM32 LLDP/CDP keychain device | Prototype |
| prtg-import | Bulk PRTG device import from CSV | Production |
| kml | KML/topology generation utilities (JBLM) | Utility |
| cert-manager | Employee training cert tracker | v0 |
| project-creation | Post-award Cyber SharePoint and Planner provisioning (Graph app-only auth, SharePoint resolver) | Scaffolding — no CLI run command yet |
| account-store | Shared user account management library | Library |
| ssi-design-system | SSi brand tokens + CSS + doc generation | v0.1 |
| claude-sync | Syncthing conflict resolver for ~/.claude | v1 |
| claude-memory-compiler | Hook-captured Claude conversations → compiled knowledge articles | v0 |
| floor-plan-editor | 2D/3D floor plan editor → HA card export | **Not on this Mac** — see note below |
| niagara-docs | Niagara 4.10/4.15 runtime binary cache + Supervisor backup (dev reference, not a project) | Stub |
| niagara-llm | CASCADE — external LLM analysis brain for Niagara BAS (oBIX/REST-BQL/SQL); FDD + LLM diagnosis, air-gapped local LLM (Ollama), Supervisor audit CLI, backup assessment; backup parser/classifier extracted to niagara-config (consumed via shims); offline diagnosis scorer (`diag-score` + `FixtureSource`) grades detection against digital-twin's labeled fixtures; dashboard API sends portfolio-baseline security headers (CSP/X-Frame-Options/etc. via `api/security_headers.py`, mirroring project-tracking; HSTS opt-in behind `SECURE_HSTS`) | v2 |
| niagara-config | Shared library: Niagara Supervisor backup (`config.bog`) parser + point→equipment/role semantic classifier; extracted from niagara-llm, consumed by niagara-llm (shims) and digital-twin | Library |
| sanguine | Internal Levels.com-style blood-lab results viewer (PDF/CSV + Apple Health import, optimal vs standard ranges, trends, biomarker detail pages, PhenoAge biological age, vitals, Claude-generated cached explanations) | v1 |
| siem-forwarder | Niagara 4 JACE module forwarding point + alarm events to a SIEM over RFC 5424 syslog/TLS, non-interference design (audit/platform logs deliberately left to Niagara's native remote syslog; `forwardAudit` exists as a config slot but is not acted on) | Skeleton/design-complete |
| scribe | SSI Scribe — self-hosted AI meeting note taker: Whisper/MLX ASR, pyannote diarization, Ollama gpt-oss:120b summaries (own repo: github.com/ogreen111/scribe) | v0.1 |
| scripts | Mount automation + Bash utilities (own repo: github.com/ogreen111/og-scripts, lives at `~/dev/scripts`) | Active |

---

Note: this "scripts" registry entry (`~/dev/scripts`, its own `og-scripts`
repo) is unrelated to `~/Documents/dev/scripts/` — dev-portfolio's own
untracked, gitignored local tooling directory (`migrate-project.sh`,
`codex-pre-commit-review.sh`, etc.). They share a name but are different
directories with different origins; the registry entry was never part of
dev-portfolio's own tracked history and needed no relocation.

**`floor-plan-editor` is missing from this Mac (noticed 2026-08-06).** All 30
other registry entries resolve to a real directory under `~/dev/`; this one
resolves to nothing — not `~/dev/floor-plan-editor`, not
`~/Documents/dev/floor-plan-editor`, nowhere else under `~`. It's listed in
`.gitignore` with zero tracked files, so dev-portfolio's own history has no
copy to restore from, and it appears in **none** of the migration batches
documented below — it looks like it was simply never carried across when
everything else moved out of `~/Documents/dev`. Since this machine is the
one that runs behind the Mac Studio, check there (and Time Machine) before
treating it as lost. Left in the registry rather than deleted, because the
registry is the portfolio's source of truth for what *should* exist.

Also present under `~/dev/` but deliberately **not** registry entries:
`sops`, `stream-deck`, and `trim-backup` (untracked, gitignored plain
directories — `stream-deck` is a real, buildable Elgato plugin and is the
strongest candidate for promotion into the registry), plus the empty
`niagara-mcp-integration` directory and the repo's own `deploy/` and
`docs/`.

## Shared Dependencies

- **account-store** → consumed by: rfp-automation, project-tracking, email-processor, past-performance, project-monitor, cert-manager, project-creation, digital-twin (`twin/auth.py`, imported by `twin/web.py` and the admin/session routes)
- **ssi-design-system** → `apps.json` marks six consumers enabled: project-tracking (the v0 pilot), rfp-automation, email-processor, cyber-artifact-gen, digital-twin, and floor-plan-editor. Synced brand bundles are present on disk in project-tracking, rfp-automation, cyber-artifact-gen, digital-twin, and **scribe** (scribe carries a bundle but has no `apps.json` entry — it drifts on every rebuild until it's added).
  - ⚠️ **`sync.py` is broken post-migration.** `apps.json`'s `_root` is still `/Users/ogreen/Documents/dev`, and `sync.py` resolves every target as `_root / name / target`. Since no consumer lives there anymore, a sync run skips all of them with "app directory not found". Fix is a one-line `_root` change to `/Users/ogreen/dev` — plus deciding what to do about the `floor-plan-editor` entry, which is enabled but has no directory anywhere (see the note above).
- **rfp-automation** → consumed by: project-creation (a `[tool.uv.sources]` path dependency alongside account-store, so project-creation needs both siblings checked out)
- **virtual-devices** → pairs with: digital-twin (frcs-digital-twin) for integration testing (see `virtual-devices/INTEGRATION.md`)
- **niagara-config** → consumed by: niagara-llm (via re-export shims), digital-twin (config-driven mode, now including backup history replay — `HistoryReplaySource` reads `niagara_config.backup.csv_history_lookup`'s CSV format)
- **digital-twin labeled fixtures** (`config export-fixtures`) → consumed by: niagara-llm (`diag-score` offline diagnosis scoring). JSON files are the decoupling contract — no live server, no runtime dependency between the repos.

_Archived 2026-07-14: **cyber-proposals** (removed), **cyber-eac-tool** (`_archive/cyber-eac-tool-20260711.tar.gz`), **cyber-estimates** (`_archive/cyber-estimates-20260714.tar.gz`). The navfac cyber proposal/pricing logic now lives in the `navfac-cyber-proposal` Claude skill._

---

## Common Tech Patterns

- **Backend:** Python + FastAPI; uv for dependency management
- **Frontend:** Vanilla JS or React/Vite/TypeScript; Tabulator 5.5 for tables; HTMX for lightweight UIs
- **Document generation:** python-docx (Python) + docx.js (Node.js)
- **AI:** Claude API with prompt caching throughout
- **Storage:** SQLite (structured), JSON (config/accounts), OneDrive/Syncthing (cross-machine)
- **OT/BAS:** bacpypes3, BAC0, Scapy, nmap, netmiko
- **Testing:** pytest; most production apps have 30–1800+ tests

---

## rfp-automation lives outside this tree

As of 2026-08-05, **rfp-automation is no longer under `~/Documents/dev/`** —
it was relocated in full to `~/dev/rfp-automation` to get it off iCloud
entirely, which makes the `.venv.nosync` workaround below moot for that
project (nothing there is iCloud-synced anymore) — but its venv still uses
the same `.venv → .venv.nosync` symlink layout for consistency with the rest
of the portfolio's tooling. `~/dev` is the separate `dev-portfolio` git repo;
`rfp-automation/` is listed
in its `.gitignore` so the moved project's files (including CUI-bearing
`projects/`) never enter that repo's tracked history. All 8 launchd agents
(dashboard, watcher, sentryloop, logrotate, optimizeloop, plannerchrome,
portalchrome, dashboard-healthcheck) and their `output/live_monitor/` plist
sources were repointed at the new path; `account-store` (a dependency, not
moved at the time) was still referenced from its original
`~/Documents/dev/account-store` absolute path — superseded once
account-store itself moved, see "account-store migrated, all 8 dependents
re-pointed" below. Start sessions for this project from
`~/dev/rfp-automation`, not here.

## niagara-config, niagara-docs, niagara-llm, niagara-mcp-integration live outside this tree

As of 2026-08-05, these four are no longer under `~/Documents/dev/` — moved
to `~/dev/` for the same iCloud reasons as rfp-automation above. All are
listed in `~/dev/.gitignore`. No launchd agents reference any of them (the
`actions.runner.ogreen111-niagara-llm.*` self-hosted CI runner clones from
GitHub, not the local path, so it's unaffected). `niagara-llm`'s server was
stopped and restarted from the new location (still port 8770); its
dependency on `niagara-config` (`pyproject.toml`'s
`niagara-config = { path = "../niagara-config", editable = true }`) is a
relative path that still resolves since both moved as siblings. `git
worktree repair` was run on both `niagara-config` and `niagara-llm` (3
linked worktrees under `niagara-llm/.claude/worktrees/`) to fix the
absolute-path worktree admin links.

Moving `niagara-docs` (134GB) and `niagara-llm` (837MB, several worktrees)
surfaced a real gotcha: **plain `mv` deadlocks on the `rename()` syscall**
for anything under the iCloud-synced `~/Documents/dev`, even when `stat -f`
shows the source and `~/dev` on the same device — iCloud's file-provider
daemon still intercepts and can hang indefinitely. `ditto` (copy via
read/write syscalls, APFS clone-aware so it's still fast) avoids the
coordinator entirely; used for all four moves here, each verified
(file-count diff, git HEAD/status match, or per-file size diff for
niagara-docs) before deleting the source. A pre-existing
`~/Documents/dev/scripts/migrate-project.sh` (built per
`.plans/dev-relocation/`, a broader, partially-executed multi-project
relocation plan authored 2026-08-01 — Batch 0 done, batches 1+ not yet run
at the time) used plain `mv` and would have hit the same deadlock — it was
patched to use `ditto` before running any further batches, and every batch
after this one used the patched script. Also: two stray,
already-hung `mv` background processes (targeting `project-tracking` and,
separately, `niagara-docs`) were found and killed during this session's
move without having touched any data — one predated this session
entirely, the other was this session's own first (later-abandoned) attempt
at `niagara-docs` before switching to `ditto`.

## digital-twin lives outside this tree

As of 2026-08-05, **digital-twin is no longer under `~/Documents/dev/`** —
it was relocated in full (the `frcs-digital-twin/` git repo, plus the
untracked `supporting/` architecture docs) to `~/dev/digital-twin/` via
`ditto`, verified by file-count/size diff and git HEAD/status match against
the Documents copy before deleting the source. `~/dev` is the separate
`dev-portfolio` git repo; `digital-twin/` is listed in its `.gitignore` so
the moved project's files never enter that repo's tracked history. The
`niagara-config` dependency fix mentioned above (`requirements.txt` pinned
to the absolute path `-e /Users/ogreen/dev/niagara-config`) was still
uncommitted in the old Documents copy — carried over to the new location as
uncommitted changes rather than reverted to a relative path, kept absolute
for consistency with how `account-store` is referenced elsewhere in the
portfolio. The `com.ssi.digital-twin` launchd agent (port 8080; not running
at move time) was repointed at the new path. Start sessions for this
project from `~/dev/digital-twin/frcs-digital-twin`, not here.

---

## project-tracking lives outside this tree

As of 2026-08-05, **project-tracking is no longer under `~/Documents/dev/`** —
it was relocated in full to `~/dev/project-tracking` to get it off iCloud
entirely, which makes the `.venv.nosync` workaround below moot for that
project (nothing there is iCloud-synced anymore) — its venv was rebuilt
fresh at the new path rather than moved, but still uses the same
`.venv → .venv.nosync` symlink layout for consistency with the rest of the
portfolio's tooling. `~/dev` is the separate `dev-portfolio` git repo;
`project-tracking/` was already listed in
its `.gitignore` so the moved project's files never enter that repo's tracked
history. All 4 launchd agents (project-tracking, project-tracking-snapshot,
project-tracking-sage-prewarm, project-tracking-exec-report) and their
`~/Library/LaunchAgents/*.plist` sources were repointed at the new path;
`account-store` (a dependency, not moved at the time) was referenced from
its original `~/Documents/dev/account-store` absolute path via a symlink
into the new venv's site-packages per `AGENTS.md`'s setup recipe —
superseded once account-store itself moved; see "account-store migrated,
all 8 dependents re-pointed" below, which recreated this exact symlink
pointing at `~/dev/account-store`. Start sessions for this project from
`~/dev/project-tracking`, not here.

## email-processor lives outside this tree

As of 2026-08-05, **email-processor is no longer under `~/Documents/dev/`** —
it was relocated in full to `~/dev/email-processor` via `ditto`, verified by
byte-level `diff -rq` (18,474 entries, clean) and git HEAD match against the
Documents copy before deleting the source. The repo had uncommitted changes
at move time (`git stash -u`, popped back cleanly at the new location — same
working-tree diff before and after). `~/dev` is the separate `dev-portfolio`
git repo; `email-processor/` is listed in its `.gitignore` so the moved
project's files never enter that repo's tracked history. Both LaunchAgents
(`com.ssi.email-intake.webserver`, `com.ssi.email-intake.watcher`) and
`scripts/webserver-entrypoint.sh`'s working directory were repointed at the
new path.

This was the project noted below as "partially migrated" (`.venv.nosync`
alongside a plain, un-symlinked `.venv`, skipped earlier because its server
was running from `.venv`) — that's now resolved. Moving broke the console
scripts: Python venv entry points (`.venv/bin/email-intake`, etc.) bake in an
absolute shebang to the venv's own interpreter at creation time, so it kept
crash-looping (`Failed to spawn: email-intake ... No such file or
directory`) even after the plist/entrypoint repointing above succeeded.
Fixed by rebuilding the venv fresh at the new path: `uv sync --dev` (plain
`uv sync`, without `--dev`, silently skipped installing the project's own
`email-intake` console script — this project's Makefile always uses `--dev`,
so match it, not the shorter recipe below), then re-editable-installed
`account_store` (`uv pip install --python .venv/bin/python -e
~/Documents/dev/account-store` — not a `pyproject.toml` dependency, so `uv
sync` alone never restores it) from its still-unmoved original location, then
fixed a stray real `.venv` directory left over from an earlier `uv sync` run
back into the intended `.venv → .venv.nosync` symlink. Both LaunchAgents were
bounced (`bootout` + `bootstrap`) and confirmed running with live PIDs
afterward; `make serve`/`make watch-once`/etc. still apply the
`chflags nohidden .venv/lib/python*/site-packages/*.pth` workaround this
project's own Makefile documents, so prefer those over a bare `uv run`. Start
sessions for this project from `~/dev/email-processor`, not here.

## cert-manager lives outside this tree

As of 2026-08-05, **cert-manager is no longer under `~/Documents/dev/`** —
it was relocated in full to `~/dev/cert-manager` via `ditto`, verified by
byte-level `diff -rq` (21,233 entries, clean) and git HEAD match against the
Documents copy before deleting the source. The repo had one uncommitted
change (`CLAUDE.md` doc updates), stashed before the move and popped back
cleanly at the new location. `~/dev` is the separate `dev-portfolio` git
repo; `cert-manager/` is listed in its `.gitignore` so the moved project's
files never enter that repo's tracked history. Both LaunchAgents
(`com.ssi.cert-manager-frontend`, `com.ssi.cert-manager-backend`) were
repointed at the new path.

Same stale-shebang fallout as email-processor above hit `backend/.venv`
(`.venv/bin/uvicorn`'s shebang still pointed at the deleted
`.../Documents/dev/cert-manager/backend/.venv/bin/python3.14`, so the
backend crash-looped even after the plist repointing succeeded) — but this
project isn't part of the `.venv.nosync` convention at all (plain `.venv`,
no `uv`), so the fix was the project's own documented recipe instead:
`rm -rf backend/.venv && cd backend && python3 -m venv .venv &&
.venv/bin/pip install -e ".[dev]"`. `backend/pyproject.toml`'s
`account-store @ file:///Users/ogreen/Documents/dev/account-store`
dependency needed no change at the time — that absolute path was still
correct since account-store hadn't moved yet (superseded once it did; see
"account-store migrated, all 8 dependents re-pointed" below, which fixed
this exact line to `~/dev/account-store`). Both LaunchAgents were bounced (`bootout` +
`bootstrap`) and confirmed live: backend `GET /api/health` → `200
{"status":"ok"}`, frontend → `200`. A `watcher: CERT_ROOT does not exist`
line in the backend log is unrelated to this move — `CERT_ROOT` points into
`~/Library/CloudStorage/OneDrive-...`, not `Documents/dev`, and just wasn't
mounted/synced at the time. Start sessions for this project from
`~/dev/cert-manager`, not here.

## network-scanner lives outside this tree

As of 2026-08-05, **network-scanner is no longer under `~/Documents/dev/`** —
relocated in full to `~/dev/network-scanner` via `ditto` (9,988 entries,
byte-identical, HEAD match). Was checked out on a feature branch
(`inventory-baseline-and-scan-runs`), not `main`, at move time - clean and
fully pushed there too. A pre-existing nested Claude Code worktree at
`.claude/worktrees/hopeful-benz-342a84` (detached HEAD, no uncommitted
changes, commit fully pushed) had to be removed with `git worktree remove`
first - its presence trips `git worktree repair`'s side effect of mutating
that worktree's own `.git` file mid-run, which then fails the script's final
pre-deletion diff check (see the `migrate-project.sh` commit history for the
general writeup). Also cleared 4 stale root-owned `__pycache__/*.pyc` files
(gitignored, safe to delete, blocked `ditto` with "Permission denied") left
over from some earlier process that ran with elevated privileges. The
`com.ssi.network-scanner` LaunchAgent wasn't loaded before the move (reason
unclear) - loaded manually afterward and confirmed serving (`GET /` → 200 on
:8000, via the LaunchAgent's `.venv/bin/python -m uvicorn` invocation - it
doesn't route through a console-script wrapper, so no venv rebuild was
needed for it). `.venv/bin/python` itself is a relative symlink chain
(`python -> python3.14 -> /opt/homebrew/...`), so that invocation form
survived the move intact - but this venv's console-script wrappers
(`.venv/bin/uvicorn`, `.venv/bin/pip`, etc.) still have the same stale
absolute shebang as every other project's here, so don't invoke them
directly; the Port Map's start command below uses the same `python -m`
form as the LaunchAgent for exactly this reason. Start sessions for
this project from `~/dev/network-scanner`, not here.

## past-performance lives outside this tree

As of 2026-08-05, **past-performance is no longer under `~/Documents/dev/`** —
relocated in full to `~/dev/past-performance` via `ditto` (9,694 entries).
Had substantial uncommitted work at move time (an in-progress session-auth
feature - `app/auth.py`, `tests/test_auth.py`, etc., 11 modified + 4
untracked files) plus a stray untracked `.pp_index.sqlite.corrupt-...` debug
artifact - stashed (in two passes; a first `git stash -u` didn't pick up
`.pp_auth/` and a `.bak-orphanfix-...` file for unclear reasons, needed an
explicit pathspec on a second pass) and restored cleanly at the new
location, working tree matching exactly. Same nested-worktree removal as
network-scanner above (`.claude/worktrees/competent-wilson-86dd33`, same
safe-to-remove profile: detached HEAD, clean, fully pushed). Same
stale-shebang fallout as email-processor/cert-manager hit `.venv/bin/uvicorn`
- fixed the same way as cert-manager (plain `python3 -m venv .venv`, no
`uv`/`.venv.nosync` convention here), plus a manual `account_store` editable
reinstall from its still-unmoved original location (also undocumented in
this project's own setup docs, like email-processor). LaunchAgent confirmed
live (`GET /` → 200 on :8767); its startup log's "removed: 29" is normal
reconciliation against the live OneDrive PP folder, unrelated to the move.
Start sessions for this project from `~/dev/past-performance`, not here.

## claude-sync lives outside this tree

As of 2026-08-05, **claude-sync is no longer under `~/Documents/dev/`** —
relocated in full to `~/dev/claude-sync` via `ditto` (2,717 entries).
Cleanest of this batch: clean tree modulo one uncommitted `CLAUDE.md` doc
change (stashed/restored), no nested worktrees, all 3 LaunchAgents
(`com.ogreen.claude-sync`, `.healthcheck`, `.menubar`) repointed and reloaded
without incident. `.venv/bin/python3` is a relative symlink, same as
network-scanner, so no shebang fallout. Confirmed live via its own startup
log (watching `~/.claude/projects`, HTTP bound on :8866). Start sessions for
this project from `~/dev/claude-sync`, not here.

## scribe lives outside this tree

As of 2026-08-05, **scribe is no longer under `~/Documents/dev/`** - its own
separate repo (github.com/ogreen111/scribe), relocated in full to
`~/dev/scribe` via `ditto` (44,333 entries). Already using both the
`.git -> .git.nosync` and `.venv -> .venv.nosync` conventions before this
move. A local branch `slice-08-observability` (one commit, never pushed) had
to be pushed to origin first to satisfy the preflight check. Migrating an
already-`.git.nosync`-converted repo surfaced two real `migrate-project.sh`
bugs, fixed in that script's own commit: `git worktree list` resolves the
main worktree's path through the `.git.nosync` symlink rather than reporting
the repo root, and `diff -rq`'s directory-loop detection false-positives on
any directory reachable two ways within the same parent - hit here on
`.git.nosync`, `.venv.nosync`, and the Swift Package Manager
`.build/debug -> arm64-.../debug` convenience symlinks. The venv was rebuilt
with the project's real production extras (`pip install -e
".[mlx,diarization,dev]"`, matching `deploy/install.sh`'s step 2, not the
minimal dev recipe) - `ssi-scribe doctor` confirmed ffmpeg, MLX ASR,
diarization, OCR, and the shared LLM all healthy afterward, with cached
models (`~/.cache/huggingface`, unaffected by the move) reused without
re-downloading. LaunchAgent confirmed live over HTTPS (`GET /` → 200 on
:8736, real LAN client traffic visible in logs immediately). Start sessions
for this project from `~/dev/scribe`, not here.

## cyber-artifact-gen, daily-summary, cyber-brain, outlook-followup, kml live outside this tree

As of 2026-08-05, these five are no longer under `~/Documents/dev/` — moved
to `~/dev/` in a batch. Much smoother than prior batches: none have
LaunchAgents, none had nested Claude Code worktrees, and only
`cyber-artifact-gen` had uncommitted work (4 modified SSi brand-bundle
files, stashed/restored cleanly). `cyber-brain` has no `.venv` yet on this
machine (never synced here), so `uv run` will build one fresh with no
stale-path risk. `outlook-followup` and `kml` have **no `.git` of their
own** — both are listed in this repo's own `.gitignore` with zero tracked
files (`git ls-files` confirms), so they moved as plain files with no
push-safety check possible (the script's documented behavior for non-git
projects) rather than as independent repos.

Two remaining projects in the registry, **`PRTG Import`** and
**`Pocket Probe`**, have spaces in their directory names and can't be
migrated via `migrate-project.sh` as-is — its own project-name safety regex
(`^[A-Za-z0-9._-]+$`) rejects them outright. Rename (or extend the script)
before attempting either.

**`account-store`** was deliberately deferred past every routine batch
above because of its shared-dependency blast radius. While deferred, a
bridge symlink (`~/dev/account-store -> ~/Documents/dev/account-store`,
added to `.gitignore` **without** a trailing slash - the trailing-slash
form doesn't match a symlink, same gotcha as `.venv*` below) let
relative-path consumers like `project-monitor`/`project-creation` resolve
it correctly from their new `~/dev/` locations in the meantime. See
"account-store migrated, all 8 dependents re-pointed" below for the full
resolution, including why that symlink turned out not to be a durable fix
on its own.

## ssi-design-system, claude-memory-compiler, sanguine, project-monitor live outside this tree

As of 2026-08-05, these four are no longer under `~/Documents/dev/` — moved
to `~/dev/` in a batch. `ssi-design-system` and `sanguine` both had a
pre-existing nested Claude Code worktree needing `git worktree remove`
first (same safe profile as prior batches); `ssi-design-system` also had an
untracked brand-asset folder (`2022 Spectrum Logos/`, legitimate content,
stashed/restored). `sanguine` separately turned up three *orphaned*
`.claude/worktrees/*` directories whose `.git` files point at
**dev-portfolio's own** (already-deleted) worktree admin data, not
sanguine's - inert leftover clutter from some earlier session, carried
along by `ditto` as-is; not a sanguine or migration problem, left alone.

All three with a `.venv` had the same stale-shebang fallout as every prior
batch - `uv sync` alone often reports success ("Checked N packages")
without actually regenerating console scripts if it thinks the lockfile is
already satisfied, so a clean `rm -rf .venv .venv.nosync && uv sync` (per
each project's own README) was needed, not just a plain re-sync.
`claude-memory-compiler` was the one exception: its `bin/uvr.sh` wrapper
deliberately keeps its uv-managed venv entirely outside the synced tree
(`UV_PROJECT_ENVIRONMENT=~/.local/share/uv-venvs/claude-memory-compiler`),
so there was no in-project venv to rebuild at all - just `PROJECT_DIR` in
that wrapper script itself needed the path fix (missed by the script's
`EXTRA_FIXUP_FILES` pass because the file was untracked and got stashed
away *before* the copy ran, then restored after - had to be re-applied by
hand). More importantly, **`~/.claude/settings.json`'s own SessionStart /
PreCompact / SessionEnd hook commands hardcoded the old absolute path** to
`bin/uvr.sh` - entirely outside any project tree the migration script could
see, so it would have silently broken the memory-compiler's automatic
flush hooks on every future session event. Fixed by hand and verified
(`hooks/session-start.py` runs correctly from the new path).

## ethernet-link-analyzer, virtual-devices, trim-backup, sops, stream-deck, fulcrum-replacement live outside this tree

As of 2026-08-05, these six are no longer under `~/Documents/dev/` — moved
to `~/dev/` in a batch. `sops`, `stream-deck`, and `fulcrum-replacement`
have no `.git` of their own (gitignored, untracked plain directories, same
as `outlook-followup`/`kml` earlier). `ethernet-link-analyzer` had a
nested Claude Code worktree (`.claude/worktrees/vibrant-rubin-571ac8`,
branch `claude/vibrant-rubin-571ac8`) with **real uncommitted work** (4
modified files, an in-progress LLDP/parser fix) - unlike every prior
nested-worktree case, which were all clean/detached-HEAD. Handled by
stashing inside the worktree, removing it, migrating, then recreating the
worktree at the new location on the same branch (`git worktree add`) and
popping the stash back - fully verified identical afterward. `virtual-devices`
and `ethernet-link-analyzer` both had stale-shebang venvs, rebuilt per
each project's own documented recipe (the latter has a real macOS +
Python 3.14 hidden-`.pth` gotcha independent of iCloud - see its own
README - requiring `chflags -R nohidden .venv` after install).

**Also discovered this round: `deploy` is *not* an independent project
either** - like `siem-forwarder`, it has no `.git` of its own and is
**not** gitignored: its 1 tracked file (`com.ssi.portfolio.plist` - this
portfolio's own LaunchAgent, doesn't belong anywhere else) lives directly
in dev-portfolio's own history. Don't run `migrate-project.sh` on it -
`git ls-files <dir>` first on any project without its own `.git` before
attempting to move it. (`project-creation` was in this same category -
see below for how it was resolved.)

## project-creation extracted into its own repo

As of 2026-08-05, **`project-creation` is no longer tracked inside
dev-portfolio at all** - like `siem-forwarder` and `deploy` above, it had
no `.git` of its own but (unlike `sops`/`stream-deck`/`fulcrum-replacement`)
27 files were tracked directly in this repo's own history (5 commits of
real work: scaffold, Graph app-only auth, SharePoint resolver). Rather
than just moving it as plain files and losing that history, it was
properly extracted:

- `git subtree split --prefix=project-creation -b project-creation-extract`
  rewrote those 5 commits with `project-creation/` stripped from every
  path, producing a standalone-ready branch.
- A new private GitHub repo was created
  (`github.com/ogreen111/project-creation`, matching every other real
  project's `github.com/ogreen111/<name>` pattern) and the extracted
  branch pushed to it as `main`.
- `project-creation/` was `git rm -r --cached` from dev-portfolio (both
  local clones - see the `~/Documents/dev` vs `~/dev` note above) and
  added to `.gitignore`, same as every migrated project. The untracked
  `.plans/` planning docs (never tracked here, per this repo's own
  gitignore convention) were copied over by hand since `subtree split`
  only carries tracked history.
- **Caution if you ever do this again:** don't run `git remote
  add`/`remote remove` from inside a subdirectory that has no `.git` of
  its own - it silently falls through to the *parent* repo's git context.
  Hit this live: a `cd project-creation && git remote add origin
  <new-repo>` actually repointed `~/dev`'s own dev-portfolio remote before
  it was caught and fixed. Always clone the extracted branch into a
  **separate, unrelated path** (e.g. the scratchpad) first, configure its
  remote there, and only move it into `~/dev/<name>` after the source has
  been fully removed from dev-portfolio's tracking.
- `pyproject.toml` has two relative-path dependencies -
  `account-store = { path = "../account-store", ... }` and `rfp-automation
  = { path = "../rfp-automation", ... }` - both resolve correctly from
  `~/dev/project-creation` (the former via the bridge symlink documented
  above, the latter since `rfp-automation` already lives at
  `~/dev/rfp-automation` for real). `uv sync --extra dev` (Python 3.12,
  auto-fetched by uv) didn't create the `.venv` symlink on its own again
  (same as `sanguine` earlier) - created by hand. Verified: all three
  modules import, 50 tests collect.

## siem-forwarder extracted into its own repo

As of 2026-08-05, **`siem-forwarder` is no longer tracked inside
dev-portfolio at all** - same situation and same fix as `project-creation`
above: 20 files and 5 real commits (Niagara bind-point resolution, alarm
forwarding, two bug fixes, an SDD sync) were tracked directly in this
repo's history with no independent `.git`. Extracted via `git subtree
split --prefix=siem-forwarder`, pushed to a new private repo
(`github.com/ogreen111/siem-forwarder`), removed from dev-portfolio's
tracking and added to `.gitignore`. The untracked
`siemForwarder-SDD-AddendumA.docx` was copied over by hand, same reason as
`project-creation`'s `.plans/`. This one had no nested worktree and no
`.plans/`, so it was simpler - but the extracted branch was still cloned
into the scratchpad first, not directly into `~/dev/siem-forwarder`,
per the gotcha documented above.

Unlike every other migrated project, **this one can't be build-verified
here**: `build.gradle` requires Tridium's Niagara Gradle plugin, resolved
from a licensed Niagara 4.10+ install via the `niagara_home` env var
(local dev bundle, not Maven Central) - not present in this environment.
Verification stopped at file-level (`diff -rq --no-dereference` clean,
correct 5-commit history, correct paths) rather than a working build.

**Also investigated and resolved differently: `deploy` is not a
project at all.** Its one tracked file, `com.ssi.portfolio.plist`, is
dev-portfolio's *own* LaunchAgent config for its portfolio index dashboard
(`~/dev/portfolio_server.py`, port 8737 - see Port Map). It correctly
lives inside dev-portfolio permanently, like `scripts/` - there's nothing
to extract or migrate. Confirmed the tracked copy has drifted slightly
from what's actually installed at `~/Library/LaunchAgents/` (a stale
comment block about TLS handling) - worth a `cp` sync on next touch, but
that's routine drift, not a migration blocker.

## pocket-probe and prtg-import live outside this tree (renamed, spaces removed)

As of 2026-08-05, the two projects with spaces in their directory names
(previously listed as `PRTG Import` and `Pocket Probe` in the registry
table above, now renamed there too) are now
`~/dev/pocket-probe` and `~/dev/prtg-import` - `migrate-project.sh`'s own
project-name safety regex (`^[A-Za-z0-9._-]+$`) rejects spaces outright, so
both were renamed to kebab-case (matching this portfolio's convention)
before migrating. Neither rename needed a GitHub rename to match: PRTG
Import's remote was already `PRTG-Import` (hyphenated); Pocket Probe never
had one (see below).

**`Pocket Probe`'s git history was corrupted** - `git status` failed with
"fatal: bad object HEAD", `git fsck` found the ref pointing at a
nonexistent commit and dozens of missing blobs, and no remote had ever
been configured. The reflog showed only 2 commits ever existed ("Initial
commit" and "Add README and MIT LICENSE", both from May). Investigated a
Time Machine recovery path (`tmutil listbackups` showed history back to
June 3, which postdates both commits) but the backup destination wasn't
actually mounted/browsable in this environment. **Critically, the
*working-tree files* were completely unaffected by the git corruption** -
`.gitattributes`, `LICENSE`, `README.md`, and the full KiCad
hardware/STM32 firmware source (1013 files) were all intact; only the
version-history metadata was broken, and only 2 small early commits'
worth of it. Resolved by backing up the broken `.git` (see
`pocket-probe/`'s own git reflog - it's a fresh history now, so the old
one isn't visible there) and reinitializing fresh from the intact working
tree as a single commit. Given a real backup, created
`github.com/ogreen111/pocket-probe` (private) this time and pushed.

**`PRTG Import` had a real, substantial merge conflict** - local `main`
and `origin/main` had diverged since May: origin had a large refactor
(site-based grouping, dry-run mode, hardened API, ~965 lines across all 3
tracked files) that local had never pulled, while local had a smaller
recent commit (a new `PRTGreport.ps1` uptime-report script, purely
additive - no actual file overlap) plus 299 lines of *stashed, never
committed* work based on the old pre-refactor files. The commit-level
merge (refactor + new report script) applied cleanly with zero real
conflicts - `git merge-tree` initially looked like it conflicted, but
that was a misread of its normal informational merge-result diff, not an
actual `CONFLICT` marker. The *stashed* uncommitted work was the real
conflict (7 blocks in `PRTGimport.ps1`, 6 in `README.md`, 1 in the config
example) - it added a `-ValidateOnly` parameter that overlapped in intent
with the refactor's independently-added `-DryRun`, among other
CSV-field-flexibility and dedup logic. Rather than guess at reconciling
PowerShell logic across two independently-evolved feature sets, dropped
the stash and kept only the clean merge - the `-ValidateOnly` work (and a
"Tracker Sync" README section documenting `sync-tracker.py`/`gap-report.py`,
which still exist as untracked files at the new location) can be
reconciled later by hand if still wanted. Also has an old orphaned nested
clone at `prtg-import/previous/` (same repo's March root commit, its own
unmerged uncommitted edits) - carried along as-is per instruction, moved
via `ditto` (not `mv` - hit the exact same iCloud cross-boundary deadlock
this whole script exists to avoid, moving it to the scratchpad and back).

## account-store migrated, all 8 dependents re-pointed

As of 2026-08-05, **`account-store` is no longer under
`~/Documents/dev/`** - relocated in full to `~/dev/account-store` via
`ditto`, the last portfolio project to move. A pre-existing nested
Claude Code worktree (`.claude/worktrees/intelligent-lalande-d5e1cd`,
detached HEAD, clean, fully pushed) was removed first, same profile as
every other one this session. The bridge symlink documented above
(`~/dev/account-store -> ~/Documents/dev/account-store`) had to be
deleted *before* running `migrate-project.sh` - the script's own
`[ -e "$NEW" ] && FATAL` check would otherwise refuse to create the real
directory at a path the symlink already occupied.

Every dependent needed re-pointing, confirmed by surveying each one's
*actual* reference mechanism rather than assuming - they turned out to be
five genuinely different patterns, not two:

1. **Hardcoded absolute path in `pyproject.toml`** (`cert-manager`) - edit
   the one line, rebuild the venv.
2. **`uv`/setuptools editable install** (`email-processor`,
   `past-performance`) - the installed `__editable__..._finder.py` bakes
   a `MAPPING` dict with the *absolute* resolved path at install time (see
   point 5 below for why this matters), so editing `pyproject.toml` alone
   does nothing; needs an actual reinstall
   (`uv pip install --python .venv/bin/python -e ~/dev/account-store`).
3. **Direct symlink into `site-packages`** (`project-tracking`, per its
   own `AGENTS.md` recipe - a Python-3.14-specific workaround for
   setuptools' editable shim dropping hidden `.pth` files) - just
   recreate the symlink at the new target.
4. **Bare `PYTHONPATH` env var**, no pip install at all (`rfp-automation`)
   - baked into 8 separate files that needed fixing in lockstep: the
   installed `~/Library/LaunchAgents/com.rfpautomation.{dashboard,watcher}.plist`
   themselves (`EnvironmentVariables.PYTHONPATH`), 5 tracked-but-gitignored
   `output/live_monitor/*.plist` mirror copies, and the actual source of
   truth, `scripts/launchd_dashboard_wrapper.sh`. That first pass still
   missed a real one - see the correction below. Editing the installed
   plists needed a full `bootout` + `bootstrap` (not `kickstart -k` -
   changed `EnvironmentVariables` needs the plist definition itself
   reloaded, not just the process restarted).
5. **`tool.uv.sources` relative path** (`project-monitor`, `project-creation`
   - `{ path = "../account-store", editable = true }`). This is the
   important one to understand: a relative source declaration does **not**
   provide ongoing resilience to account-store moving - `uv sync` still
   resolves it to an absolute path *at install time* and bakes that into
   the installed finder script, identically to pattern 2 above. The
   bridge symlink documented earlier only worked because it existed at
   the moment these were installed; once account-store moved for real and
   the symlink was removed, both needed the exact same
   `rm -rf .venv .venv.nosync && uv sync` treatment as every absolute-path
   editable install elsewhere in this portfolio - no exemption for having
   used the relative form.

All 5 live services (`cert-manager` backend, `email-processor` webserver,
`past-performance`, `rfp-automation` dashboard + watcher, `project-tracking`)
were bounced and confirmed genuinely healthy afterward, not just
"restarted": `cert-manager` `GET /api/health` → `200`; `email-processor` →
`401` (auth-gated, expected); `past-performance` → `302` (login redirect,
expected); `project-tracking` → `200` over HTTPS; `rfp-automation`
dashboard log showed the *old* process's `ModuleNotFoundError` crashes
ending precisely at the restart timestamp, with clean `200`/`303`
responses immediately after; `rfp-automation` watcher's own log showed
zero `ModuleNotFoundError` occurrences post-restart, just normal
"Using cached access token" activity.

**The first "final grep came back clean" claim here was wrong** - it used
`2>/dev/null`, which silently swallowed whatever made the wide `~/dev/`
recursive grep miss real matches it found fine when scoped to a single
project directory (never fully diagnosed; suspected resource limits on
such a large recursive tree). A Codex pre-commit review caught it live
and it's worth remembering generally: don't trust an error-suppressed
grep's silence as proof of a clean sweep, especially over a big tree.
Rerunning without suppression turned up a genuinely missed **8th
consumer, `digital-twin`** (`twin/auth.py`'s docstring, `CLAUDE.md`'s
`ln -s` recipe, a `CHANGELOG.md` mention) - not in the original 7-project
survey at all, and a real functional break: `twin/auth.py` genuinely *is*
imported (`twin/web.py` does `from . import auth` and calls
`auth.gate(request)` on every request; `twin/routes/admin.py` and
`twin/routes/session.py` import it too - a first check here that searched
for `import twin.auth`/`from twin.auth import` missed this relative-import
style entirely). Its `.venv/lib/python3.14/site-packages/account_store`
symlink existed but was stale (pointing at the deleted
`Documents/dev/account-store` - a second check here missed it too, using
`find -maxdepth 4` on a path that's actually 5 levels deep). Fixed both
and verified `twin.auth` now imports cleanly. `twin.web`'s *full* import
chain also had an unrelated, pre-existing gap at the time (`niagara_config`
not installed in this venv at all) - since resolved (see "digital-twin's
BACnet and DB issues fixed" below): `niagara_config` is now installed,
`twin.web` imports cleanly, and `com.ssi.digital-twin` is loaded and
serving the HMI. Also found and fixed real broken command examples
in `rfp-automation`'s `README.md`/`CLAUDE.md`/`AGENTS.md` and a
**functional break**: its
`.claude/launch.json` (the actual dev-server preview config used by this
harness's own `preview_start`, not just docs) had the stale `PYTHONPATH`
baked in too - fixed and committed in that repo along with the doc
fixes. `project-tracking` had four more stale doc references beyond the
two caught initially (`AGENTS.md`, `CLAUDE.md`, `README.md`, plus the
`webapp/auth.py` docstring). All three affected repos (`rfp-automation`,
`project-tracking`, `digital-twin`) got their own commits, separate from
this one. A properly-verified sweep (no `2>/dev/null`, scoped file-by-file
rather than trusting one wide recursive call) now comes back clean.

## digital-twin's BACnet and DB issues fixed

As of 2026-08-06, `com.ssi.digital-twin` is loaded and its `niagara_config`
gap (noted above) is resolved - `.venv/bin/python -c "import niagara_config"`
and `from twin import web` both succeed, and the LaunchAgent serves the HMI
on :8080. Two separate issues reported as "database corruption" and
"BACnet issues" were investigated and resolved:

- **DB "corruption"**: `twin/fdd/event_store.py`'s `EventStore` already
  self-heals via `_rebuild_if_corrupt()` (a `PRAGMA integrity_check` on
  init, discarding the DB + WAL/SHM/journal sidecars if it fails). Verified
  the live `.state.nosync/twin_events.sqlite` passes integrity check
  cleanly (145 rows) - no action needed, the existing safeguard already
  did its job.
- **BACnet init failing under launchd, but working when run interactively**:
  root cause was `~/Library/LaunchAgents/com.ssi.digital-twin.plist`'s
  `EnvironmentVariables.PATH` (`/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin`)
  missing `/sbin`, where `ifconfig` lives. `twin/controllers.py`'s
  `_autodetect_macos_iface()` shells out to `ifconfig` to work around a
  known BAC0-on-macOS netmask-detection bug; under the restricted launchd
  PATH the `ifconfig` call silently failed, `_autodetect_macos_iface()`
  returned `None`, and BAC0's own broken autodetect then threw
  `NetmaskValueError: 'None' is not a valid netmask`. Fixed by adding
  `/usr/sbin:/sbin` to the plist's `PATH` and reloading with `bootout` +
  `bootstrap` (`kickstart -k` alone doesn't pick up changed
  `EnvironmentVariables`). Confirmed via the error log: BACnet now
  auto-detects the LAN interface and comes up on port 47808. No tracked
  plist template exists in the digital-twin repo for this LaunchAgent -
  the installed copy at `~/Library/LaunchAgents/com.ssi.digital-twin.plist`
  is the only source of truth.

---

## Virtualenvs: keep them in `.venv.nosync` (iCloud workaround)

`~/Documents` is iCloud-synced on this Mac. iCloud Drive sets the macOS
`UF_HIDDEN` flag on everything beneath dot-named directories (`.venv`, `.git`,
...) and re-applies it within ~0.5s of `chflags nohidden`, so clearing flags is
futile. Python 3.11+ silently skips hidden `.pth` files, which breaks editable
installs (`ModuleNotFoundError` from `.venv/bin/...` console scripts while
`uv run` still works). Directories ending in `.nosync` are excluded from iCloud
entirely and never get flagged.

- `UV_PROJECT_ENVIRONMENT=.venv.nosync` is exported in `~/.zshenv` (relative
  path → resolved per-project), so `uv sync`/`uv run` create venvs at
  `<project>/.venv.nosync`.
- Each migrated project keeps a `.venv → .venv.nosync` symlink so existing
  `.venv/bin/...` commands (e.g. the Port Map below) keep working.
- Migrating an existing project: `rm -rf .venv .venv.nosync && uv sync && ln -s .venv.nosync .venv`
  (only when nothing is running from the venv). Removing only the `.venv`
  symlink and leaving `.venv.nosync` in place lets `uv sync` reuse the
  moved environment as-is instead of rebuilding it — console-script
  shebangs baked in at the old path stay stale. Ensure `.gitignore` uses
  `.venv*`, not `.venv/` (a symlink isn't matched by the trailing-slash form).
- Migrated so far: project-monitor, ssi-design-system, niagara-llm, sanguine,
  digital-twin/frcs-digital-twin, rfp-automation, project-tracking,
  email-processor, scribe (`.venv` is a symlink to `.venv.nosync`).
- Don't write per-file workarounds (runtime import shims, chflags hooks) —
  they lose the race or rot.

---

## `.git` lives in `.git.nosync` (same iCloud workaround)

The repo's own `.git` directory hit the identical failure mode as venvs: iCloud
duplicated files inside it (refs, `COMMIT_EDITMSG`, etc.) when it didn't like
concurrent access, producing broken-named refs (`refs/heads/main 2`, `main 3`)
and `git branch -a` warnings. Fixed 2026-08-03 the same way as venvs:

- The real git directory was moved to `~/Documents/dev/.git.nosync`; `.git` at
  the repo root is now a symlink to it (`.git -> .git.nosync`).
- This is safe for the repo's many linked worktrees: each linked worktree's own
  `.git` file hardcodes an absolute path like
  `gitdir: /Users/ogreen/Documents/dev/.git/worktrees/<name>`, which still
  resolves correctly through the `.git` symlink — no worktree files needed
  updating.
- `.gitignore` has a `.git.nosync` entry so the real directory doesn't show up
  as a giant untracked folder in `git status` (git only auto-hides the literal
  `.git` path, not a renamed one).
- Verified fixed via the same test as venvs: `chflags nohidden` on a file
  inside `.git.nosync` did not get reverted after a couple seconds (an
  actively-synced item reverts within ~0.5s).
- If this repo is ever re-cloned or a new worktree tooling flow bypasses the
  symlink, redo the same move: `mv .git .git.nosync && ln -s .git.nosync .git`
  (only when no git operation is in progress and no lockfiles exist).

---

## Port Map

Reserved ports for the dev portfolio. Each app binds its assigned port on startup; do not double-book.

| Port | Project | Service | Start command |
|---|---|---|---|
| 8000 | network-scanner | FastAPI backend | `cd ~/dev/network-scanner && .venv/bin/python -m uvicorn scanner.app:app --host 0.0.0.0 --port 8000` (not `.venv/bin/uvicorn` directly - that console script has a stale shebang) |
| 8002 | cert-manager | FastAPI backend | `cd ~/dev/cert-manager/backend && .venv/bin/uvicorn app.main:app --port 8002` |
| 8008 | rfp-automation | dashboard (stdlib HTTP) | `cd ~/dev/rfp-automation && .venv/bin/rfp-auto dashboard` (reads `RFP_DASHBOARD_PORT` from `.env`) |
| 8080 | digital-twin | Flask HMI | `cd ~/dev/digital-twin/frcs-digital-twin && WEB_HMI_PORT=8080 .venv/bin/python -m twin.cli run` |
| 8081 | digital-twin | Niagara oBIX server (emulator) | `cd ~/dev/digital-twin/frcs-digital-twin && TWIN_ENABLE_NIAGARA=1 .venv/bin/python -m twin.cli run` (gated by `TWIN_ENABLE_NIAGARA=1`) |
| 8082 | digital-twin | Niagara REST/BQL endpoint (emulator) | same process as oBIX above (`NIAGARA_BQL_PORT`) |
| 8736 | scribe | uvicorn terminates TLS directly (mkcert cert), no reverse proxy | LaunchAgent `com.ssi.scribe` (https://host:8736) |
| 8737 | dev-portfolio | Plain HTTP (`ThreadingHTTPServer`), no TLS — `PORTFOLIO_SSL_CERTFILE`/`KEYFILE` are set but `portfolio_server.py` never reads them (details/caveats: [PORTS.md](PORTS.md)) | `launchctl kickstart -k gui/$(id -u)/com.ssi.portfolio` (binds 0.0.0.0:8737) |
| 8765 | email-processor | FastAPI + uvicorn | `cd ~/dev/email-processor && make serve` (applies the `chflags nohidden` .pth workaround; a bare `uv run` re-hides the file on its next sync) |
| 8767 | past-performance | FastAPI + uvicorn | `cd ~/dev/past-performance && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8767` |
| 443 | project-tracking | uvicorn terminates TLS directly (mkcert cert), no reverse proxy — cutover complete 2026-07-06, the old plaintext `:8768` endpoint is retired (see `project-tracking/docs/DEPLOYMENT.md`) | LaunchAgent `com.ssi.project-tracking` (https://og-work-mac-studio.local/ or https://10.10.10.92/) |
| 8769 | project-monitor | FastAPI + uvicorn | `cd ~/dev/project-monitor && PM_PORT=8769 .venv/bin/project-monitor run` |
| 8770 | niagara-llm | FastAPI + dashboard | `cd ~/dev/niagara-llm && uv run niagara-llm run` |
| 8771 | sanguine | FastAPI + dashboard | `cd ~/dev/sanguine && uv run sanguine run` (reads `SANGUINE_PORT`) |
| 8772 | cyber-brain | FastAPI + dashboard | `cd ~/dev/cyber-brain && uv run cyber-brain run` (reads `CB_HOST`/`CB_PORT`; binds 127.0.0.1 by default) |
| 8773 | project-creation | FastAPI (default `PROJECT_CREATION_PORT`) | reserved — `project_creation.app:create_app()` exists but the CLI (`project-creation`) is still a stub with no `run`/uvicorn wiring yet |
| 8774 | fulcrum-replacement | FastAPI + offline-first mobile app (planned) | reserved only — `fulcrum-replacement/` has no `pyproject.toml` or app code yet, just `DESIGN.md`/`DESIGN.docx`; no start command exists until it's built |
| 5173 | cert-manager | Vite frontend (proxies `/api` → 8002) | `cd ~/dev/cert-manager/frontend && npm run dev` |

**Notes:**

- past-performance, project-tracking, and email-processor all default to 8765 in their own READMEs; the portfolio-wide assignment moves them apart so they can run simultaneously.
- cert-manager's Vite proxy target in `frontend/vite.config.ts` must match the backend port (currently `8002`).
- **Avoid port 8766** — silently reserved at the OS level on this machine (visible via `netstat` as LISTEN on `127.0.0.1:8766` but with no `lsof`-visible owner).
- The `claude-sync` daemon binds `127.0.0.1:8866` (not a portfolio app server, but reserves the port).

---

## Key Files

- `README.md` — full project index with descriptions
- `PROJECTS_SUMMARY.md` — compact per-project summary (auto-generated)
- `DESIGN.docx` — portfolio architecture doc (data flows, shared libs, roadmap)
- `PROJECTS_SUMMARY.docx` — same content as PROJECTS_SUMMARY.md in Word format

---

## Sliced Project Plans

When the user asks to create, save, or prepare an execution plan for a project, prefer a local sliced plan under the project root:

- Create a `./.plans/` directory in the project.
- Add `./.plans/` to the project `.gitignore` when the project is a git repository, unless the user explicitly wants plans committed.
- Split the plan into numbered markdown slices named in execution order, such as `01-config.md`, `02-core-logic.md`, and `03-docs-validation.md`.
- Each slice should include goal, dependencies, files/entry points, implementation steps, tests, validation, and done criteria.
- Add `./.plans/PLAN.md` as the index and orchestration file. It should briefly describe each slice, state the required execution order, and call out which slices can be done in parallel.
- Keep slices small enough for an LLM or agent to execute independently, with clear contracts between slices.
- If the project is not a git repository or `.gitignore` cannot be updated safely, mention that in the final response.
