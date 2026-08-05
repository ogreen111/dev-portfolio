# Dev Portfolio — Claude Context

This directory (`~/Documents/dev/`) is the root of a personal development workspace containing 31 projects built around three core domains:

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
| outlook-followup | Outlook follow-up automation | Stub |
| past-performance | SSi past-performance doc search + extraction | v1 |
| project-tracking | Job budget/cost/labor/submittal dashboard; React v2 UI primary, Planner/SharePoint Graph sync | v1 |
| project-monitor | Project folder + Outlook email → PM status via entity registers (contracts, mods, POs, invoices, pay apps) | v2 |
| cyber-brain | SSi cyber group knowledge system: Graph ingestion (SharePoint/Planner/Teams/email) → per-project event stream, briefs, cited Q&A | v0.1 |
| daily-summary | Power Automate daily email digest solution | v0 |
| fulcrum-replacement | Offline-first mobile field data collection platform (Fulcrum SaaS replacement) | Design only |
| network-scanner | Active network discovery + BACnet enumeration | v1 |
| ethernet-link-analyzer | Passive LLDP/CDP Ethernet discovery; Pi field appliance w/ touch UI, battery, gated active tests | Phase 4 |
| virtual-devices | BACnet/IP virtual building fleet (76 devices) | v1 |
| digital-twin | FRCS HVAC plant digital twin + fault injection; selectable twin models (office-building / barracks-cep campus, mutually exclusive, live-switchable from the HMI), electrical model, ~50-detector FDD (office-building; barracks-cep coverage partial); config-driven mode emulates a real site from a Niagara Supervisor backup (via niagara-config, designed-for future third model) — incl. per-detector role catalog + `config coverage` report, fault injection addressed by real equipment id, findings in real config names, and `config export-fixtures` labeled diagnosis fixtures | v1.12 |
| Pocket Probe | STM32 LLDP/CDP keychain device | Prototype |
| PRTG Import | Bulk PRTG device import from CSV | Production |
| kml | KML/topology generation utilities (JBLM) | Utility |
| cert-manager | Employee training cert tracker | v0 |
| project-creation | Post-award Cyber SharePoint and Planner provisioning (Graph app-only auth, SharePoint resolver) | Scaffolding — no CLI run command yet |
| account-store | Shared user account management library | Library |
| ssi-design-system | SSi brand tokens + CSS + doc generation | v0.1 |
| claude-sync | Syncthing conflict resolver for ~/.claude | v1 |
| claude-memory-compiler | Hook-captured Claude conversations → compiled knowledge articles | v0 |
| floor-plan-editor | 2D/3D floor plan editor → HA card export | Active |
| niagara-docs | Niagara 4.10/4.15 runtime binary cache + Supervisor backup (dev reference, not a project) | Stub |
| niagara-llm | CASCADE — external LLM analysis brain for Niagara BAS (oBIX/REST-BQL/SQL); FDD + LLM diagnosis, air-gapped local LLM (Ollama), Supervisor audit CLI, backup assessment; backup parser/classifier extracted to niagara-config (consumed via shims); offline diagnosis scorer (`diag-score` + `FixtureSource`) grades detection against digital-twin's labeled fixtures; dashboard API sends portfolio-baseline security headers (CSP/X-Frame-Options/etc. via `api/security_headers.py`, mirroring project-tracking; HSTS opt-in behind `SECURE_HSTS`) | v2 |
| niagara-config | Shared library: Niagara Supervisor backup (`config.bog`) parser + point→equipment/role semantic classifier; extracted from niagara-llm, consumed by niagara-llm (shims) and digital-twin | Library |
| sanguine | Internal Levels.com-style blood-lab results viewer (PDF/CSV + Apple Health import, optimal vs standard ranges, trends, biomarker detail pages, PhenoAge biological age, vitals, Claude-generated cached explanations) | v1 |
| siem-forwarder | Niagara 4 JACE module forwarding point/alarm/audit events to a SIEM over RFC 5424 syslog/TLS, non-interference design | Skeleton/design-complete |
| scribe | SSI Scribe — self-hosted AI meeting note taker: Whisper/MLX ASR, pyannote diarization, Ollama gpt-oss:120b summaries (own repo: github.com/ogreen111/scribe) | v0.1 |
| scripts | Mount automation + Bash utilities | Active |

---

## Shared Dependencies

- **account-store** → consumed by: rfp-automation, project-tracking, email-processor, project-monitor, cert-manager, project-creation
- **ssi-design-system** → consumed by: project-tracking, (planned for all SSi web apps)
- **virtual-devices** → pairs with: digital-twin (frcs-digital-twin) for integration testing (see `virtual-devices/INTEGRATION.md`)
- **niagara-config** → consumed by: niagara-llm (via re-export shims), digital-twin (config-driven mode)
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
moved) is still referenced from its original `~/Documents/dev/account-store`
absolute path. Start sessions for this project from `~/dev/rfp-automation`,
not here.

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

**digital-twin still lives in `~/Documents/dev/` and depends on
`niagara-config` via a relative path** (`frcs-digital-twin/requirements.txt`:
`-e ../../niagara-config`) that broke when niagara-config moved out from
under it. Fixed by switching to an absolute path
(`-e /Users/ogreen/dev/niagara-config`), matching how `account-store` is
already referenced across the portfolio. If digital-twin itself is ever
moved, revisit this back to a relative path.

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
relocation plan authored 2026-08-01 — Batch 0 done, batches 1+ not yet run)
uses plain `mv` and will hit the same deadlock — worth patching to use
`ditto` before that plan's remaining batches run. Also: two stray,
already-hung `mv` background processes (targeting `project-tracking` and,
separately, `niagara-docs`) were found and killed during this session's
move without having touched any data — one predated this session
entirely, the other was this session's own first (later-abandoned) attempt
at `niagara-docs` before switching to `ditto`.

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
`account-store` (a dependency, not moved) is still referenced from its
original `~/Documents/dev/account-store` absolute path, symlinked into the
new venv's site-packages per `AGENTS.md`'s setup recipe. Start sessions for
this project from `~/dev/project-tracking`, not here.

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
- Migrating an existing project: `rm -rf .venv && uv sync && ln -s .venv.nosync .venv`
  (only when nothing is running from the venv). Ensure `.gitignore` uses
  `.venv*`, not `.venv/` (a symlink isn't matched by the trailing-slash form).
- Migrated so far: project-monitor, ssi-design-system, niagara-llm, sanguine,
  digital-twin/frcs-digital-twin, rfp-automation, project-tracking (`.venv` is
  a symlink to `.venv.nosync`). Partially migrated (`.venv.nosync` exists
  alongside a plain, un-symlinked `.venv`) — migrate on next touch:
  email-processor (skipped because its server was running from `.venv`).
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
| 8000 | network-scanner | FastAPI backend | `cd network-scanner && .venv/bin/uvicorn scanner.app:app --host 0.0.0.0 --port 8000` |
| 8002 | cert-manager | FastAPI backend | `cd cert-manager/backend && .venv/bin/uvicorn app.main:app --port 8002` |
| 8008 | rfp-automation | dashboard (stdlib HTTP) | `cd ~/dev/rfp-automation && .venv/bin/rfp-auto dashboard` (reads `RFP_DASHBOARD_PORT` from `.env`) |
| 8080 | digital-twin | Flask HMI | `cd digital-twin/frcs-digital-twin && WEB_HMI_PORT=8080 .venv/bin/python -m twin.cli run` |
| 8081 | digital-twin | Niagara oBIX server (emulator) | `cd digital-twin/frcs-digital-twin && TWIN_ENABLE_NIAGARA=1 .venv/bin/python -m twin.cli run` (gated by `TWIN_ENABLE_NIAGARA=1`) |
| 8082 | digital-twin | Niagara REST/BQL endpoint (emulator) | same process as oBIX above (`NIAGARA_BQL_PORT`) |
| 8736 | scribe | uvicorn terminates TLS directly (mkcert cert), no reverse proxy | LaunchAgent `com.ssi.scribe` (https://host:8736) |
| 8737 | dev-portfolio | Plain HTTP (`ThreadingHTTPServer`), no TLS — `PORTFOLIO_SSL_CERTFILE`/`KEYFILE` are set but `portfolio_server.py` never reads them (details/caveats: [PORTS.md](PORTS.md)) | `launchctl kickstart -k gui/$(id -u)/com.ssi.portfolio` (binds 0.0.0.0:8737) |
| 8765 | email-processor | FastAPI + uvicorn | `cd email-processor && uv run email-intake serve` |
| 8767 | past-performance | FastAPI + uvicorn | `cd past-performance && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8767` |
| 8768 | project-tracking | FastAPI + uvicorn | `cd ~/dev/project-tracking && PT_PORT=8768 .venv/bin/python -m webapp` |
| 8769 | project-monitor | FastAPI + uvicorn | `cd project-monitor && PM_PORT=8769 .venv/bin/project-monitor run` |
| 8770 | niagara-llm | FastAPI + dashboard | `cd ~/dev/niagara-llm && uv run niagara-llm run` |
| 8771 | sanguine | FastAPI + dashboard | `cd sanguine && uv run sanguine run` (reads `SANGUINE_PORT`) |
| 8772 | cyber-brain | FastAPI + dashboard | `cd cyber-brain && uv run cyber-brain run` (reads `CB_HOST`/`CB_PORT`; binds 127.0.0.1 by default) |
| 8773 | project-creation | FastAPI (default `PROJECT_CREATION_PORT`) | reserved — `project_creation.app:create_app()` exists but the CLI (`project-creation`) is still a stub with no `run`/uvicorn wiring yet |
| 8774 | fulcrum-replacement | FastAPI + offline-first mobile app (planned) | reserved only — `fulcrum-replacement/` has no `pyproject.toml` or app code yet, just `DESIGN.md`/`DESIGN.docx`; no start command exists until it's built |
| 5173 | cert-manager | Vite frontend (proxies `/api` → 8002) | `cd cert-manager/frontend && npm run dev` |

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
