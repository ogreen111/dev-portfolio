# Dev Portfolio — Claude Context

This directory (`~/Documents/dev/`) is the root of a personal development workspace containing 32 projects built around three core domains:

1. **DoD/MILCON cybersecurity proposal automation** — RFP intake → pricing → tech proposal → EAC tracking
2. **BAS/OT network engineering** — passive discovery, BACnet simulation, site scanning, hardware prototypes
3. **SSi internal productivity** — email triage, project financial tracking, past-performance management

---

## Project Registry

| Project | Purpose | Status |
|---|---|---|
| rfp-automation | DoD RFP intake, scope extraction, proposal drafting | Production |
| cyber-proposals | Shared proposal engine (MRR + UMCS MATOCs) | Production |
| cyber-estimates | Per-solicitation proposal artifact generation | Active |
| cyber-eac-tool | Earned-value forecasting (EAC/ETC/CPI/SPI) | Active |
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
| digital-twin | FRCS HVAC plant digital twin + fault injection; campus multi-RTU mode, electrical model, ~50-detector FDD | v1.10 |
| Pocket Probe | STM32 LLDP/CDP keychain device | Prototype |
| PRTG Import | Bulk PRTG device import from CSV | Production |
| kml | KML/topology generation utilities (JBLM) | Utility |
| cert-manager | Employee training cert tracker | v0 |
| account-store | Shared user account management library | Library |
| ssi-design-system | SSi brand tokens + CSS + doc generation | v0.1 |
| claude-sync | Syncthing conflict resolver for ~/.claude | v1 |
| claude-memory-compiler | Hook-captured Claude conversations → compiled knowledge articles | v0 |
| floor-plan-editor | 2D/3D floor plan editor → HA card export | Active |
| niagara-docs | Niagara 4.10/4.15 runtime binary cache + Supervisor backup (dev reference, not a project) | Stub |
| niagara-llm | CASCADE — external LLM analysis brain for Niagara BAS (oBIX/REST-BQL/SQL); FDD + LLM diagnosis, air-gapped local LLM (Ollama), Supervisor audit CLI, backup assessment | v2 |
| sanguine | Internal Levels.com-style blood-lab results viewer (PDF/CSV + Apple Health import, optimal vs standard ranges, trends, biomarker detail pages, PhenoAge biological age, vitals, Claude-generated cached explanations) | v1 |
| siem-forwarder | Niagara 4 JACE module forwarding point/alarm/audit events to a SIEM over RFC 5424 syslog/TLS, non-interference design | Skeleton/design-complete |
| scribe | SSI Scribe — self-hosted AI meeting note taker: Whisper/MLX ASR, pyannote diarization, Ollama gpt-oss:120b summaries (own repo: github.com/ogreen111/scribe) | v0.1 |
| scripts | Mount automation + Bash utilities | Active |

---

## Shared Dependencies

- **account-store** → consumed by: rfp-automation, project-tracking, email-processor, project-monitor
- **ssi-design-system** → consumed by: project-tracking, (planned for all SSi web apps)
- **cyber-proposals** → consumed by: cyber-estimates, rfp-automation (adapter)
- **virtual-devices** → used by: network-scanner for integration testing

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
- Migrated so far: project-monitor, ssi-design-system. Others still have plain
  `.venv` dirs with flagged `.pth` files — migrate on next touch
  (email-processor was skipped because its server was running from `.venv`).
- Don't write per-file workarounds (runtime import shims, chflags hooks) —
  they lose the race or rot.

---

## Port Map

Reserved ports for the dev portfolio. Each app binds its assigned port on startup; do not double-book.

| Port | Project | Service | Start command |
|---|---|---|---|
| 8000 | network-scanner | FastAPI backend | `cd network-scanner && .venv/bin/uvicorn scanner.app:app --host 0.0.0.0 --port 8000` |
| 8002 | cert-manager | FastAPI backend | `cd cert-manager/backend && .venv/bin/uvicorn app.main:app --port 8002` |
| 8008 | rfp-automation | dashboard (stdlib HTTP) | `cd rfp-automation && .venv/bin/rfp-auto dashboard` (reads `RFP_DASHBOARD_PORT` from `.env`) |
| 8010 | cyber-eac-tool | local Excel/edit server | `cd cyber-eac-tool && .venv/bin/python serve.py --port 8010` |
| 8080 | digital-twin | Flask HMI | `cd digital-twin/frcs-digital-twin && WEB_HMI_PORT=8080 .venv/bin/python -m twin.cli run` |
| 8081 | digital-twin | Niagara oBIX server (emulator) | `cd digital-twin/frcs-digital-twin && TWIN_ENABLE_NIAGARA=1 .venv/bin/python -m twin.cli run` (gated by `TWIN_ENABLE_NIAGARA=1`) |
| 8082 | digital-twin | Niagara REST/BQL endpoint (emulator) | same process as oBIX above (`NIAGARA_BQL_PORT`) |
| 8736 | scribe | app terminates its own TLS (uvicorn, mkcert cert) — no proxy | LaunchAgent `com.ssi.scribe` (https://host:8736) |
| 8737 | dev-portfolio | portfolio index/doc server terminates its own TLS (mkcert cert) — no proxy | LaunchAgent `com.ssi.portfolio` (https://host:8737) |
| 8765 | email-processor | FastAPI + uvicorn | `cd email-processor && uv run email-intake serve` |
| 8767 | past-performance | FastAPI + uvicorn | `cd past-performance && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8767` |
| 8768 | project-tracking | FastAPI + uvicorn | `cd project-tracking && PT_PORT=8768 .venv/bin/python -m webapp` |
| 8769 | project-monitor | FastAPI + uvicorn | `cd project-monitor && PM_PORT=8769 .venv/bin/project-monitor run` |
| 8770 | niagara-llm | FastAPI + dashboard | `cd niagara-llm && uv run niagara-llm run` |
| 8771 | sanguine | FastAPI + dashboard | `cd sanguine && uv run sanguine run` (reads `SANGUINE_PORT`) |
| 8772 | cyber-brain | FastAPI + dashboard | `cd cyber-brain && uv run cyber-brain run` (reads `CB_HOST`/`CB_PORT`; binds 127.0.0.1 by default) |
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
