# Dev Folder Project Summary

A summary of all 31 registry projects, generated 2026-08-06.

**Projects now live under `/Users/ogreen/dev/`, not `/Users/ogreen/Documents/dev/`.**
The sub-projects were relocated off the iCloud-synced tree on 2026-08-05; this
repo retains only the portfolio-level docs. Start sessions from
`~/dev/<project>`. The one exception is `floor-plan-editor`, which is in the
registry but resolves to no directory under `~/dev/` — see its entry below.
See `CLAUDE.md` for per-project migration history.

---

## account-store
**Purpose:** Shared Python package for local user account management with pbkdf2_sha256 password hashing. Extracted from rfp-automation.
**Stack:** Python (pip-installable), JSON-backed storage, pbkdf2_sha256.
**Notes:** Reusable library with role-based access (admin/reviewer/viewer) and legacy migration. 26 tests. The portfolio's most widely shared dependency — 8 consumers: rfp-automation, project-tracking, email-processor, past-performance, project-monitor, cert-manager, project-creation, digital-twin. Consumers bind it five different ways (absolute path, editable install, `site-packages` symlink, bare `PYTHONPATH`, `tool.uv.sources` relative path); none survive the library moving without a reinstall.

## cert-manager
**Purpose:** Web app to manage employee training certificates in a shared folder. Parses certificate contents (filename + PDF text + OCR), tracks expiration, and serves a React UI for viewing/filtering.
**Stack:** FastAPI (Python backend), React + Vite + TypeScript, SQLite.
**Notes:** v0.0.1 with invite-based auth, multi-stage parsing (regex filename → PDF text → Tesseract OCR → review queue), TTL-driven expiry, watchdog real-time folder sync, bulk operations, CSV export, and a person × cert-type matrix view; Tailwind + shadcn/ui components; account-store auth. Ports 8002/5173. Only 7 tests — the thinnest suite of any production-facing app here.

## claude-memory-compiler
**Purpose:** Personal knowledge base that automatically compiles Claude Code conversations into searchable structured articles. Conversations are captured via hooks, flushed to daily logs, and compiled into cross-referenced knowledge articles with health checks.
**Stack:** Python 3.12+, Claude Agent SDK; no vector DB or RAG.
**Notes:** v0 prototype; session → flush → compile → query → lint pipeline; installed across 3 Macs via iCloud-synced tree. Unusual in keeping its uv venv outside the project tree (`bin/uvr.sh` sets `UV_PROJECT_ENVIRONMENT`), and in being driven by `~/.claude/settings.json`'s SessionStart/PreCompact/SessionEnd hooks rather than launched directly.

## claude-sync
**Purpose:** macOS daemon that resolves Syncthing conflict files in `~/.claude/projects/` using per-glob merge strategies (3-way merge for memory files, newest-mtime for regenerable files).
**Stack:** Python, Syncthing, launchd agents, git merge-file.
**Notes:** Dual-Mac synchronization with health monitoring; includes healthcheck + menu bar app; 230-test suite. Structured logging + SQLite sink added June 2026. Binds 127.0.0.1:8866. Stable — no commits since 2026-05-30.

## cyber-artifact-gen
**Purpose:** Converts Niagara BAS network exports to hardware/software diagrams and network schematics for DoD cyber proposals.
**Stack:** Python scripts, ad-hoc JSON/CSV processing.
**Notes:** Utility scripts for document generation; brand/a11y contrast updates June 2026. No README. Design-system integration is data-level only — `scripts/ssi_naming.py` validates JACE names against the SSi station convention, while eMASS HW/SW lists and Visio diagrams deliberately keep their DoD/template styling and are *not* recolored.

## cyber-brain
**Purpose:** Knowledge management system for the SSi cyber & integration group. Ingests Microsoft Graph data (SharePoint, Planner, Teams transcripts, email) into a normalized per-project SQLite event stream with FTS5, then generates onboarding briefs, answers questions with citations, and produces digests.
**Stack:** Python 3.11+ (FastAPI, msal/Graph SDK, SQLite FTS5, extract-msg, PyPDF).
**Notes:** v0.1 prototype; CUI-aware handling; CSV ingestion added July 2026; 89 tests across 13 files; web UI on port 8772. Quiet since 2026-07-01.

## daily-summary
**Purpose:** Power Automate solution for an automated daily email digest, packaged as a Microsoft solution zip.
**Stack:** Power Automate (Microsoft cloud workflow engine).
**Notes:** v0; no development since May 2026. Ships as `DailySummary_1_0_0_21.zip` plus `source/` and `docs/`; no README, no git repo of its own.

## digital-twin
**Purpose:** FRCS digital twin of a small commercial HVAC plant (17,500 ft², 50-ton CW plant). Synthetic physics + BACnet/IP emulation with Flask/HTMX HMI for operator training and fault-injection scenarios.
**Stack:** Python (BAC0, Flask, Click), BACnet/IP, Modbus/TCP, HTMX + Three.js 3D graphics.
**Notes:** Product name **DOPPEL**. Revision 2.15 (unreleased line; 1.9 was the last tagged release) with major 2026 expansion: selectable twin models (office-building / barracks-cep campus, mutually exclusive, live-switchable from the HMI), full electrical distribution model (breaker trip logic, sub-metering), black start with motor inrush + standby generator/ATS, PI/PID supervisory control, FDD engine + probabilistic diagnoser, Niagara oBIX/REST-BQL emulation layer, N4 Px generator. Config-driven mode (via `niagara-config`) emulates a specific real site from a Niagara Supervisor backup — publishing real point names/topology, physics where modeled + a coverage dial elsewhere (opt-in via `TWIN_FROM_BACKUP` + `TWIN_ENABLE_NIAGARA`). Config-mode FDD validation adds a per-detector equipment/role catalog, a `config coverage` report, fault injection addressed by real equipment id, findings named in real config terms, and `config export-fixtures` labeled diagnosis fixtures consumed by niagara-llm's scorer. Recent: rev 2.13 cross-scope cascade diagnosis (barracks + CEP), rev 2.14 open-fdd parity port (office-building detectors 54 → 65), rev 2.15 backup **history replay** — `HistoryReplaySource` interpolates real Workbench-exported histories over bound points, live (`TWIN_HISTORY_REPLAY`) or headless (`config replay-backup`). ~1,020 tests across 87 files. Ports 8080/8081/8082.

## email-processor
**Purpose:** Automated triage for inbound RFI/RFQ/RFP emails for SSi. Parses mail, fetches gated PWS/questions from GSA MRAS/SAM/eBuy/PIEE, summarizes via Claude, outputs to Obsidian vault + docx + webserver dashboard.
**Stack:** Python (uv, FastAPI, Playwright, Claude API), Obsidian output.
**Notes:** Production system, branded "Email Intake". The CMMC constraint is specifically **no Graph API and no service-principal flows** against SSI's M365 tenant: mail is read and processed locally on Owen's Mac rather than pulled from the tenant by a cloud identity. The derived artifacts (Obsidian vault, `.docx` briefs) do then sync between his machines over OneDrive, so mail-derived content does leave the Mac — it's the tenant-access path that's constrained, not the storage. Dashboard with auth (port 8765); v2 watcher + portal fetchers landed June 2026. Emits a structured `pursue-prime` / `pursue-sub` / `watch` / `pass` call with fit assessment against SSI's capability lanes. ~420 tests across 32 files. Use `make serve` / `make watch-once`, not a bare `uv run` (the Makefile applies the hidden-`.pth` `chflags` workaround).

## ethernet-link-analyzer
**Purpose:** Passive Ethernet discovery tool for enterprise/government/OT networks. Identifies upstream switch, port, VLANs, voice VLAN, and management IPs from LLDP/CDP traffic. Raspberry Pi field appliance with touch UI, web HMI, and PiSugar battery management.
**Stack:** Python (Scapy, libpcap, BPF), OUI lookup, rich, JSON export; SPI touchscreen + WiFi AP mode on the appliance.
**Notes:** v0.2.0. Phases 1–2 complete, Phase 3 (Pi field appliance) largely complete; Phase 4 in progress (long-duration monitoring, ARP host inventory, baseline/drift anomaly detection). Zero-transmit by default; the only exception is an operator-gated active-test mode (connectivity, PHY cable test, speed qualification), off by default, warned in the UI, and logged per run. Explicit non-goals: not a cable tester, not a port scanner, not a switch management tool. ~250 tests across 21 files.

## floor-plan-editor
**Purpose:** Single-file web app for editing 2D floor plans, viewing in 3D dollhouse, exporting Home Assistant picture-elements cards. Built from RoboRock vacuum maps.
**Stack:** HTML5 + JavaScript (Three.js), localStorage, SVG export.
**Notes:** ⚠️ **Not present on this Mac (noticed 2026-08-06).** Every other registry entry resolves to a directory under `~/dev/`; this one resolves to nothing, and it appears in none of the documented migration batches. Gitignored with zero tracked files, so this repo has no copy to restore from. Check the Mac Studio and Time Machine before treating it as lost. Still listed as an enabled `ssi-design-system` consumer in that project's `apps.json`.

## fulcrum-replacement
**Purpose:** In-house offline-first mobile field data collection platform (iOS/Android) to replace the ~$40k/yr Fulcrum subscription. Covers BAS asset surveys, JACE commissioning checklists, and QC inspections.
**Stack (proposed):** Capacitor (React/Vite mobile wrapper), FastAPI + PostGIS backend, durable offline SQLite.
**Notes:** Design stage only — the directory holds nothing but `DESIGN.md` and `DESIGN.docx` (rev 4, 2026-07-02) with requirements, ROI analysis (~14–15 month payoff), and an offline-durability risk spike. No `pyproject.toml`, no app code, no git repo of its own; port 8774 is reserved but no start command exists.

## kml
**Purpose:** Utilities for parsing and generating KML files, Niagara network topology, and building centroids from JBLM (Joint Base Lewis-McChord) commissioning data.
**Stack:** JavaScript (KML generation), Python (JBLM parsing), CSV/xlsx input.
**Notes:** Utility collection for a specific site deployment; loose scripts, CSV/xlsx exports, and generated KML sitting side by side. No README and no git repo of its own — gitignored plain files. Data dates to 2020; no active development.

## network-scanner
**Purpose:** Laptop-based network discovery and switch interrogation. Scans devices, ports, services; enumerates BACnet/IP; imports baselines from CSV/xlsx; provides web UI and CLI.
**Stack:** Python (nmap, netmiko, bacpypes3, FastAPI), SQLite, HTMX + Jinja templates.
**Notes:** v1, framed as an RMF cyber-audit tool for BAS networks and built to support the WPAFB AFRL EMMS RMF proposal. Site-based scans + profiles (a "safe" OT profile avoids known embedded HTTP stack crashes); BACnet Who-Is + ReadProperty enumeration; credentialed Windows/WinRM interrogation; TLS/SSH auditing; YAML-driven CVE matching against every captured banner; NIST 800-53-grouped risk register + RMF markdown report; Ruckus FastIron SPAN session builder; pure-Python PCAP decoding with protocol-aware findings. ~430 tests across 42 files; includes WPAFB BAS network simulator (76 devices). Port 8000 — start with `.venv/bin/python -m uvicorn`, not `.venv/bin/uvicorn` (stale shebang).

## niagara-config
**Purpose:** Shared Python library that parses Niagara Supervisor backups (`config.bog`) and classifies station points into an equipment/role semantic model. Extracted from niagara-llm to be a single source of truth for Niagara-backup handling.
**Stack:** Python (pydantic only), hatchling.
**Notes:** Library, v0.1.0, 30 tests. Public API across `backup`/`semantic`/`model`/`topology`/`catalog`/`sources.base`. Consumed by niagara-llm (via re-export shims, so its existing imports are unchanged) and by digital-twin's config-driven mode. Its `semantic` `Role`/`EquipType` values are the canonical vocabulary both consumers bind to — digital-twin's FDD detector catalog validates its declared point roles against them, and its `backup.csv_history_lookup` format is what digital-twin's rev-2.15 history replay reads. Created 2026-07.

## niagara-docs
**Purpose:** Local reference cache of Niagara 4.10/4.15 runtime binaries (bin/lib/modules) plus a Supervisor backup, used for developing the Niagara-facing projects.
**Stack:** — (binary cache, not a codebase).
**Notes:** Stub/reference only; no active development. ~134 GB — by far the largest directory in the portfolio, and the one that most needed `ditto` rather than `mv` during the migration off iCloud.

## niagara-llm
**Purpose:** CASCADE — external analysis brain that monitors Niagara BAS stations (real-time point values + historical trends) for issues via Niagara-faithful interfaces (oBIX, REST/BQL, SQL history export) behind a single `StationDataSource` abstraction; ports to a real JACE/Supervisor by config change.
**Stack:** Python (FastAPI, httpx, Ollama local LLM, Claude API), SQLite, Docker appliance bundle.
**Notes:** v2 — fully air-gapped local-LLM operation, adaptive baselines, RAG-grounded diagnosis; current phase is closed-loop write-back + fleet monitoring + operator dashboard. Includes Supervisor audit CLI (federation/architecture/security analyzers) and backup-assessment ROI reporting. The Supervisor-backup parser + semantic classifier were extracted (2026-07) into the shared `niagara-config` library, now consumed via re-export shims. Developed against digital-twin's Niagara emulation (FaultEngine as test oracle); a `diag-score` CLI + `FixtureSource` now grade detection offline against digital-twin's labeled diagnosis fixtures (JSON files are the decoupling contract — no live server needed). The README maintains a deliberately evidence-qualified validation table: backup ingestion and native `.hdb` decoding are *backup-validated* (four backup families, 1,368–109,042 points); oBIX `/points` + JSON-BQL are *twin-validated*; one authorized Niagara 4.15 lab station is *live-validated* for verified-TLS lobby discovery plus a bounded 43-point catalog and read; real histories, alarms, and sustained soak are *pilot pending*; write-back is *experimental*, disabled and dry-run by default. Don't replace those labels with a generic "complete." ~960 tests across 110 files. Port 8770.

## outlook-followup
**Purpose:** "Follow-Up Reminder" — an Office.js add-in *intended* to flag sent emails for follow-up and remind you if no reply arrives within a configurable window. Ribbon button plus compose-time tracking, optional `OnMessageSend` auto-tracking, a dashboard taskpane with overdue badge, and three parallel reminder channels (Outlook flag with due date, Microsoft To Do task, dashboard). Reply detection is meant to scan the conversation via Microsoft Graph, with the tracked list syncing across devices via `roamingSettings`. Targets Outlook on the web, new Outlook for Mac, and Outlook for Windows.
**Stack:** Office.js add-in — JS + webpack + `manifest.xml`, `office-addin-debugging` npm scripts (`build`, `start`, `validate`, `sideload:mac`); `followup-addin/` plus a packaged `.zip`.
**Notes:** **v1.0.0 in `package.json`, but written and apparently never run** — the old "Stub" label undersold the surface area (real README, working build wiring, ~1,300 LOC across taskpane/commands/shared) while overselling its readiness. Treat the purpose above as intent, not working behavior: two blocking defects found 2026-08-06 mean the Graph-backed half cannot function. (1) `src/shared/mailbox.js` calls `Office.auth.getAccessToken(options, callback)`, but that API is promise-only and takes no callback, so the wrapping `new Promise` never settles and `getGraphToken()` hangs forever — killing reply detection, flagging, and To Do task creation. (2) `storage.addItem()` dedups on `conversationId`, which is `null` for an unsaved compose item, so under `OnMessageSend` auto-tracking every new message collides on `null === null` and overwrites the last, with no later backfill. Both live in the add-in's own source, not this repo; left unfixed here deliberately. Also lacks a test suite and a git repo of its own. Listed as a disabled `ssi-design-system` consumer ("opt in once tested").

## past-performance
**Purpose:** Local web app that monitors a folder of SSi past-performance documents (PDF/DOCX/DOC/XLSX/TXT/MD), full-text indexes with SQLite FTS5, and provides search, faceted browsing, extraction, curation, and generation. Documents expand into individual PP records (many PPs per file), editable and mergeable inline.
**Stack:** Python (FastAPI, SQLite FTS5, mammoth, pypdf, tesseract OCR, Voyage AI embeddings, Claude API), plain JS frontend.
**Notes:** v1; Claude-assisted extraction/generation and semantic retrieval (Voyage AI, 1024-dim asymmetric) added June 2026; generated PPs export to `.docx` via SSI's template; HTML sanitized with nh3 for shared deployment. 45 tests. Port 8767.

## pocket-probe
**Purpose:** Keychain-sized network discovery device (STM32F767 firmware + KiCad hardware) that captures LLDP and CDP frames to identify upstream switches, ports, VLANs, management IPs, capabilities, and PoE info, showing them on a 1.8″ OLED with a QR code for handoff to a phone. Codename *whats-your-name*.
**Stack:** C (STM32 HAL), KiCad, Python simulators (Scapy).
**Notes:** Early-stage hardware project; firmware works on a Nucleo dev board; v0 hardware is in early schematic capture, PCB layout not started. Renamed from `Pocket Probe` (spaces blocked the migration script's name regex) and pushed to a new private repo `github.com/ogreen111/pocket-probe` in 2026-08 — its original git history was found corrupted (bad HEAD, missing blobs, no remote ever configured) and was reinitialized from the fully intact working tree, losing only 2 early commits' worth of version metadata.

## project-creation
**Purpose:** Post-award provisioning for the SSi Cyber group — stands up a project's SharePoint site and Planner plan once an award lands, using Microsoft Graph app-only auth plus a SharePoint resolver.
**Stack:** Python (FastAPI, httpx, Graph app-only auth, Jinja2, pydantic), account-store.
**Notes:** Scaffolding. `project_creation.app:create_app()` exists and port 8773 is reserved, but the `project-creation` console script is still an argparse stub with no `run`/uvicorn wiring — nothing serves yet. 46 tests. Depends on **both** `account-store` and `rfp-automation` as sibling path dependencies, so it needs both checked out next to it. Extracted out of dev-portfolio's own tracked history (5 commits, via `git subtree split`) into `github.com/ogreen111/project-creation` on 2026-08-05.

## project-monitor
**Purpose:** Monitors project document folders and Outlook email to maintain per-project entity registers (contracts, mods, ASIs, POs, invoices, pay applications, completion progress) using deterministic path classifiers + Claude extraction; rolls up into program status views (web dashboard, Word report, STATUS.md).
**Stack:** Python (FastAPI, SQLite, Microsoft Graph SDK, python-docx, openpyxl, extract-msg), account-store auth.
**Notes:** v2 register architecture (shipped in four waves, June 2026) with v1→v2 migration. Emails become status *signals* on register rows rather than new items; the folder watcher uses settle-then-fire to avoid mid-sync partial reads, and the deterministic path/filename classifier runs first so Claude is asked for at most one extraction call per file. ~290 tests across 19 files. Port 8769.

## project-tracking
**Purpose:** Cross-references funding PDFs, labor PDFs, and Microsoft Planner data to produce per-job dashboards covering budget, costs, labor hours, and submittal pipeline. FastAPI web portal with role-based auth.
**Stack:** Python (FastAPI, pdfplumber, openpyxl, mpxj), React 18 (Vite + TypeScript + Tailwind), account-store.
**Notes:** v1 with the React SPA (v2 UI) now primary. 2026 additions: Microsoft Graph Planner sync, SharePoint document sourcing, per-job completion-source picker, per-phase/CLIN breakdown + contract/billing rollup from Sage exports (read live, no Reprocess), per-job ACLs + sharing ("Shared with me" tab), MS Project `.mpp` schedule integration via MPXJ with planner-vs-schedule drift flags, snapshot history, auto-refresh on file change. ~540 tests across 65 files. Port 443 (self-terminated TLS, no proxy) — the old plaintext `:8768` endpoint is retired. The `ssi-design-system` v0 pilot.

## prtg-import
**Purpose:** PowerShell script that bulk-imports devices into PRTG from a CSV. Devices route into per-site groups by /24 IP prefix, get tagged with hardware metadata, and are resumed for monitoring — all idempotently.
**Stack:** PowerShell 5.1+, PRTG API.
**Notes:** CLI automation tool; production-ready. Dry-run mode, site routing, and a hardened API path; device IP address column added June 2026. Renamed from `PRTG Import` in 2026-08 (remote was already `PRTG-Import`); the same pass merged a large long-diverged origin refactor back into local cleanly. A stashed 299-line `-ValidateOnly` work-in-progress was **dropped** during that merge as redundant with the refactor's `-DryRun` — reconcile by hand if still wanted. Untracked `sync-tracker.py` / `gap-report.py` helpers live alongside it, plus an orphaned nested clone at `previous/`.

## rfp-automation
**Purpose:** Automated extraction, analysis, and proposal generation for DoD/MILCON cybersecurity RFPs. Parses specs/drawings, classifies cyber governance (25 05 11 / 25 08 11), extracts scope, builds submittal matrices, generates drafts.
**Stack:** Python (PyMuPDF, python-docx, openpyxl, Playwright, Claude API), FastAPI dashboard.
**Notes:** Production system; ~4,180 tests across 234 files — the largest suite in the portfolio. Dashboard on port 8008. 2026 additions: email intake with PIID identity gate, bid follow-up tracking + Planner comments, amendment cyber review (local Ollama for CUI), redesigned dashboard with SSE live updates, per-project Ask-AI chat, SENTRY self-improvement loop (launchd), TCC-safe state dir at `~/Library/RFPAutomation/state/`.

## sanguine
**Purpose:** Internal Levels.com-style blood-lab results viewer with multi-person support: PDF/CSV + Apple Health import, optimal vs standard reference ranges (~50 biomarkers, sex-specific), trends, biomarker detail pages, and Claude-generated cached educational content.
**Stack:** Python (FastAPI, SQLite, PyMuPDF + PyPDF, pytesseract OCR, Anthropic SDK).
**Notes:** v1 (renamed from levels-labs, July 2026); PhenoAge biological age, HOMA-IR auto-computation, Centenarian Decathlon tracker, Four Horsemen risk view. One person per OAuth-authenticated user, auto-created on first login. CSV is the robust import path; PDF parsing is best-effort and reports its recognition rate. Explicitly not a clinical product. 130 tests across 14 files. Port 8771.

## scribe
**Purpose:** SSI Scribe — self-hosted, privacy-first AI meeting note taker (split out of rfp-automation into its own repo: github.com/ogreen111/scribe). Bot-free browser capture with live transcript plus recording upload, Whisper/MLX transcription, pyannote speaker diarization, and Ollama-served gpt-oss:120b structured summaries (decisions, action items with owners, recap email draft).
**Stack:** Python (FastAPI, SQLite WAL+FTS5), vanilla-JS SPA, Whisper/MLX, pyannote, Ollama.
**Notes:** v0.1; cross-meeting Ask-AI with citations, FTS5 search, talk-time analytics, tags, Word/Markdown/transcript exports. Screen captures during live recordings are snapshotted, OCR'd into search when tesseract is present, and embedded in the Word export. On Windows, sharing the whole screen with system audio captures native Zoom/Teams/Webex without any installed agent. ~460 tests across 40 files. Port 8736, with uvicorn terminating TLS directly (mkcert).

## scripts
**Purpose:** Parent workspace for script-based projects and utilities. Currently contains mount automation (sshfs mounts to Ubuntu Docker + UDM Pro).
**Stack:** Bash shell scripts, watchdog scripts.
**Notes:** Organizational container with mounts/ folder for Ubuntu/UDM automation. Its own repo (`github.com/ogreen111/og-scripts`) at `~/dev/scripts` — distinct from dev-portfolio's own untracked local tooling directory of the same name, which holds `migrate-project.sh`, `codex-pre-commit-review.sh`, and `refresh-portfolio-docs.sh`.

## siem-forwarder
**Purpose:** Niagara 4 JACE module forwarding security-relevant station events (point value/status changes and alarms) to a SIEM over RFC 5424 syslog/TLS with a non-interference design: ride-along subscriptions only, bounded drop-oldest queue, below-normal-priority worker, self-throttling with gap events. It forwards **points + alarms only** — audit/platform logs are deliberately deferred to Niagara's own native remote syslog (4.10+), since reading audit records would require Tridium-internal `com.tridium.history.audit.*` APIs; `forwardAudit` remains as a config slot but is not acted on.
**Stack:** Java (Niagara 4 module API, Gradle).
**Notes:** Skeleton/design-complete; call sites written against the Niagara 4.15.1 API surface; bind points remain for the target build (slot-o-matic, alarm/audit listener types, TLS trust store). Audit/platform logs are deliberately left to Niagara's native remote syslog to keep the custom-code surface minimal. Design doc: `siemForwarder-SDD.docx`. Extracted out of dev-portfolio's own tracked history (5 commits, `git subtree split`) into `github.com/ogreen111/siem-forwarder` on 2026-08-05. **The only project here that can't be build-verified on this Mac** — `build.gradle` needs Tridium's Niagara Gradle plugin from a licensed Niagara 4.10+ install (`niagara_home`), which isn't present; verification stops at file level.

## ssi-design-system
**Purpose:** Single source of truth for SSi brand tokens (colors, typography, spacing, radii, shadows). Consumed by SSi web + document-generation apps. Also home to the Niagara 4 engineering standard.
**Stack:** JSON tokens, CSS custom properties, Python (brand.py, build/sync scripts, Niagara artifact builders), openpyxl + python-docx, Pillow.
**Notes:** v0.1.0, Phases 1–3 complete; project-tracking is the v0 pilot. Niagara workstream: point naming contract + point dictionary, data-driven plant graphics (PNG/Px/SVG), 10 Px view templates, kitPx artwork catalog, PX_AUTHORING guide. 49 tests across 9 files. `apps.json` marks six consumers enabled (project-tracking, rfp-automation, email-processor, cyber-artifact-gen, digital-twin, floor-plan-editor); scribe carries a synced brand bundle but has no `apps.json` entry, so it drifts on every rebuild. ⚠️ **`sync.py` currently syncs to nobody** — `apps.json`'s `_root` still points at the pre-migration `/Users/ogreen/Documents/dev`, and `sync.py` resolves targets as `_root / name / target`, so every app is skipped with "app directory not found". One-line fix, plus a decision on the `floor-plan-editor` entry (enabled, but the directory doesn't exist anywhere).

## virtual-devices
**Purpose:** Fleet of BACnet/IP "virtual buildings" that share a network with a real JACE 9000. Each container = one realistic building with behavior models, point lists, and multi-vendor identity.
**Stack:** Python (bacpypes3, docker-compose), macvlan networking, 5 archetypes.
**Notes:** Linux-only (macvlan requires bridged NIC); 76 devices total, 53 BACnet-bearing; smoke test runs offline on macOS. Pairs with digital-twin for integration testing (see `INTEGRATION.md`). Stable — no commits since 2026-05-22.

---

## Not in the registry

Present under `~/dev/` but deliberately outside the 31-project registry, all
untracked and gitignored:

- **stream-deck** — SSi Deck, a custom Elgato Stream Deck plugin (`com.ssi.deck`) on the official `@elgato/streamdeck` SDK (Node 20, TypeScript + Rollup). Three actions: Portfolio Launcher (starts a portfolio service and shows a live status dot, service list mirrors the Port Map), Command Runner, and Status Tile, all drawing button faces through a shared SVG engine. Builds and validates; the strongest candidate for promotion into the registry.
- **sops** — a single Windows Server User CALs SOP in md/docx/pdf plus its `build_sop_docx.js` generator.
- **trim-backup** — docs only.
- **niagara-mcp-integration** — an empty directory.

`deploy/` and `docs/` inside this repo are not projects either: `deploy/`
holds dev-portfolio's own `com.ssi.portfolio.plist` LaunchAgent (port 8737),
and `docs/` holds orphaned-worktree rescue notes.
