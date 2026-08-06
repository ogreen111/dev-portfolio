# Dev Portfolio

Personal development workspace for tools and systems built around DoD/MILCON cybersecurity proposals, BAS/OT network engineering, and internal SSi productivity automation.

**31 projects** · Last updated 2026-08-06

> **The projects no longer live next to this file.** As of 2026-08-05 the
> sub-projects were relocated out of the iCloud-synced `~/Documents/dev/` tree
> to `~/dev/<project>` (each gitignored here, so this repo only ever tracks the
> portfolio-level docs). Start a session from `~/dev/<project>`, not from this
> directory. The one exception is `floor-plan-editor`, which is in the registry
> but has no directory under `~/dev/` — see its entry below. `siem-forwarder`
> and `project-creation` went further still, extracted into their own repos.
> See `CLAUDE.md` for the per-project migration history and gotchas.

---

## Quick Index

| Project | Category | Stack | Status |
|---|---|---|---|
| [rfp-automation](#rfp-automation) | Proposal Automation | Python, Claude API, FastAPI | Production |
| [cyber-artifact-gen](#cyber-artifact-gen) | Proposal Automation | Python | Utility |
| [email-processor](#email-processor) | SSi Productivity | Python, FastAPI, Playwright | Production |
| [outlook-followup](#outlook-followup) | SSi Productivity | Office.js add-in, webpack | ⚠️ Written, never run |
| [past-performance](#past-performance) | SSi Productivity | Python, FastAPI, SQLite | v1 |
| [project-tracking](#project-tracking) | SSi Productivity | Python, FastAPI, React | v1 |
| [project-monitor](#project-monitor) | SSi Productivity | Python, FastAPI, Graph SDK | v2 |
| [cyber-brain](#cyber-brain) | SSi Productivity | Python, FastAPI, Graph SDK | v0.1 |
| [project-creation](#project-creation) | SSi Productivity | Python, FastAPI, Graph SDK | Scaffolding |
| [daily-summary](#daily-summary) | SSi Productivity | Power Automate | v0 |
| [fulcrum-replacement](#fulcrum-replacement) | SSi Productivity | Capacitor, FastAPI, PostGIS | Design only |
| [network-scanner](#network-scanner) | Network / OT Tools | Python, FastAPI, nmap | v1 |
| [ethernet-link-analyzer](#ethernet-link-analyzer) | Network / OT Tools | Python, Scapy | Phase 4 |
| [virtual-devices](#virtual-devices) | Network / OT Tools | Python, bacpypes3, Docker | v1 |
| [digital-twin](#digital-twin) | Network / OT Tools | Python, BAC0, Flask | rev 2.15 |
| [niagara-llm](#niagara-llm) | Network / OT Tools | Python, FastAPI, Ollama, Claude API | v2 |
| [siem-forwarder](#siem-forwarder) | Network / OT Tools | Java (Niagara 4), Gradle | Skeleton/design-complete |
| [pocket-probe](#pocket-probe) | Network / OT Tools | C, KiCad, Python | Prototype |
| [prtg-import](#prtg-import) | Network / OT Tools | PowerShell | Production |
| [kml](#kml) | Network / OT Tools | JS, Python | Utility |
| [cert-manager](#cert-manager) | Platform / Shared | FastAPI, React, SQLite | v0 |
| [account-store](#account-store) | Platform / Shared | Python | Library |
| [niagara-config](#niagara-config) | Platform / Shared | Python, pydantic | Library |
| [ssi-design-system](#ssi-design-system) | Platform / Shared | JSON, CSS, Python | v0.1 |
| [claude-sync](#claude-sync) | Platform / Shared | Python, launchd | v1 |
| [claude-memory-compiler](#claude-memory-compiler) | Platform / Shared | Python, Claude Agent SDK | v0 |
| [sanguine](#sanguine) | Standalone Tools | Python, FastAPI, SQLite | v1 |
| [scribe](#scribe) | Standalone Tools | Python, FastAPI, Whisper/MLX, pyannote, Ollama | v0.1 |
| [floor-plan-editor](#floor-plan-editor) | Standalone Tools | HTML5, Three.js | ⚠️ Not on this Mac |
| [niagara-docs](#niagara-docs) | Reference | — | Stub |
| [scripts](#scripts) | Reference | Bash | Active |

---

## Categories

### Proposal Automation

Tools that automate the full DoD/MILCON cybersecurity proposal lifecycle — from RFP intake through pricing, scope extraction, and tech proposal generation.

#### rfp-automation
Automated extraction, analysis, and proposal generation for DoD/MILCON cybersecurity RFPs. Parses specs and drawings, classifies cyber governance (UFGS 25 05 11 / 25 08 11), extracts scope, builds submittal matrices, and generates draft proposals. 2026 additions: email intake with PIID identity gate, bid follow-up tracking with Planner comment integration, amendment cyber review (local Ollama for CUI, cloud otherwise), redesigned dashboard with SSE live updates, per-project Ask-AI chat, and a launchd-driven SENTRY self-improvement loop. **Stack:** Python (PyMuPDF, python-docx, openpyxl, Playwright, Claude API), FastAPI dashboard (port 8008). ~4,180 tests across 234 files — the largest suite in the portfolio.

#### cyber-artifact-gen
Converts Niagara BAS network exports to hardware/software diagrams and network schematics for use in DoD cyber proposals. **Stack:** Python scripts, JSON/CSV processing.

---

### SSi Productivity

Tools for email triage, document ingestion, past-performance tracking, project financial monitoring, and internal knowledge management.

#### email-processor
Automated triage for inbound RFI/RFQ/RFP emails at SSi. Parses mail, fetches gated documents from GSA MRAS/SAM/eBuy/PIEE portals, summarizes via Claude API, and outputs to Obsidian vault + docx + dashboard. CMMC-compliant (no Graph API). Syncs across machines via OneDrive. **Stack:** Python (uv, FastAPI, Playwright, Claude API). Port 8765. ~420 tests across 32 files.

#### outlook-followup
"Follow-Up Reminder" — an Office.js add-in *intended* to flag sent emails for follow-up and remind you if no reply arrives within a configurable window: ribbon button and compose-time tracking, optional `OnMessageSend` auto-track, a dashboard taskpane with overdue badge, and three parallel reminder channels (Outlook flag with due date, a Microsoft To Do task, and the dashboard). Reply detection is meant to scan the conversation via Microsoft Graph, with the tracked list syncing across devices through `roamingSettings`. Targets Outlook on the web, new Outlook for Mac, and Outlook for Windows. **Stack:** Office.js add-in — JS + webpack + manifest.xml, `office-addin-debugging` npm scripts (~1,300 LOC across taskpane/commands/shared). No test suite, and no git repo of its own (gitignored plain files).

> ⚠️ **Written but apparently never run.** Two blocking defects found 2026-08-06 suggest this was never exercised end-to-end, so treat the feature list above as intent, not working behavior:
> 1. `src/shared/mailbox.js` calls `Office.auth.getAccessToken(options, callback)`, but that API is promise-only — it takes no callback. The wrapping `new Promise` therefore never settles and `getGraphToken()` hangs forever, which takes every Graph-backed feature (reply detection, flagging, To Do task) with it.
> 2. `storage.addItem()` dedups by `conversationId`, which is `null` on an unsaved, brand-new (non-reply) compose item — replies already carry a real `conversationId` from their thread. Under `OnMessageSend` auto-tracking, consecutive new messages collide on `null === null` and overwrite the previous one; nothing backfills the real ID later.
>
> Both are in the add-in's own source, not in this repo — left unfixed here deliberately, since this is a docs refresh.

#### past-performance
Local web app that monitors a folder of SSi past-performance documents (PDF/DOCX/DOC/XLSX/TXT/MD), full-text indexes with SQLite FTS5, and provides search, faceted browsing, Claude-assisted extraction, and PP generation. Voyage AI embeddings power semantic retrieval of similar prior PPs when drafting new ones; output exports to `.docx` via SSI's template. **Stack:** Python (FastAPI, SQLite FTS5, mammoth, pypdf, tesseract OCR, Voyage AI, Claude API), plain JS frontend. Port 8767. 45 tests.

#### project-tracking
Cross-references funding PDFs, labor PDFs, and Microsoft Planner exports to produce per-job dashboards (budget, costs, labor hours, submittal pipeline). React SPA (v2 UI) is now the primary interface. 2026 additions: Microsoft Graph Planner sync (no manual exports), SharePoint document sourcing, per-job completion-source picker, per-phase/CLIN breakdown and contract/billing rollup from Sage exports, per-job ACLs + sharing. **Stack:** Python (FastAPI, pdfplumber, openpyxl, mpxj), React 18 (Vite + TypeScript + Tailwind), account-store auth. Port 443 (self-terminated TLS, no proxy). ~540 tests across 65 files.

#### project-monitor
Monitors project document folders and Outlook email to maintain per-project entity registers (contracts, mods, ASIs, POs, invoices, pay applications, completion progress) using deterministic path classifiers plus Claude extraction, then rolls up into program status views — web dashboard, Word report, and STATUS.md. v2 register architecture with v1→v2 migration. **Stack:** Python (FastAPI, SQLite, Microsoft Graph SDK, python-docx, extract-msg), account-store. Port 8769. ~290 tests across 19 files.

#### cyber-brain
Knowledge management system for the SSi cyber & integration group. Ingests Microsoft Graph data (SharePoint, Planner, Teams transcripts, email) into a normalized per-project SQLite event stream with FTS5, then generates onboarding briefs, answers questions with citations, and produces digests. CUI-aware handling. **Stack:** Python (FastAPI, msal/Graph SDK, SQLite FTS5, extract-msg, PyPDF). Port 8772. 89 tests. Quiet since 2026-07.

#### project-creation
Post-award provisioning for the Cyber group: stands up a project's SharePoint site and Planner plan once an award lands, using Graph app-only auth plus a SharePoint resolver. Extracted out of dev-portfolio's own history into `github.com/ogreen111/project-creation` (2026-08-05). `project_creation.app:create_app()` exists and port 8773 is reserved, but the `project-creation` console script is still an argparse stub with no `run`/uvicorn wiring — nothing serves yet. Depends on both `account-store` and `rfp-automation` as sibling path dependencies. **Stack:** Python (FastAPI, httpx, Graph app-only auth, Jinja2), account-store. 46 tests. Status: scaffolding.

#### daily-summary
Power Automate solution for an automated daily email digest, packaged as a Microsoft solution zip. **Stack:** Power Automate. Status: v0.

#### fulcrum-replacement
Design for an in-house, offline-first mobile field data collection platform (iOS/Android) to replace the ~$40k/yr Fulcrum subscription. Covers BAS asset surveys, JACE commissioning checklists, and QC inspections. **Stack (proposed):** Capacitor (React/Vite), FastAPI + PostGIS backend, durable offline SQLite. Design doc rev 4 (2026-07-02); no code yet. Proposed port 8774.

---

### Network / OT Tools

Tools for passive/active network discovery, BACnet simulation, and OT site engineering.

#### network-scanner
Laptop-based network discovery and switch interrogation. Scans devices, ports, and services; enumerates BACnet/IP; imports baselines from CSV/xlsx; provides web UI and CLI. Includes WPAFB BAS network simulator (76 devices across 5 archetypes) and field simulation / scan-run control. Positioned as an RMF cyber-audit tool for BAS networks: CVE matching against captured banners, a NIST 800-53-grouped risk register, credentialed Windows/WinRM enumeration, TLS/SSH auditing, SPAN/port-mirror session building, and pure-Python PCAP decoding with protocol-aware findings. **Stack:** Python (nmap, netmiko, bacpypes3, FastAPI), SQLite, HTMX + Jinja. Port 8000. ~430 tests across 42 files.

#### ethernet-link-analyzer
Passive Ethernet discovery for enterprise/government/OT networks. Identifies upstream switch, port, VLANs, voice VLAN, and management IPs from LLDP/CDP traffic. Phases 1–3 complete: protocol parsing (LLDP/LLDP-MED/CDP), vendor fingerprinting, multi-protocol OT presence detection, and a Raspberry Pi field appliance with touch UI, web HMI, and PiSugar battery management. Phase 4 in progress: long-duration monitoring, ARP-based host inventory, baseline/drift anomaly detection. Also includes an operator-gated active-test mode (connectivity, PHY cable test, link speed qualification) — off by default. **Stack:** Python (Scapy, libpcap, BPF), OUI lookup, rich, JSON export. v0.2.0. ~250 tests across 21 files.

#### virtual-devices
Fleet of BACnet/IP virtual buildings that share a network with a real JACE 9000. 76 total devices (53 BACnet-bearing) across 5 archetypes (office/barracks/hangar/clinic/warehouse). Linux-only (macvlan). Used for network-scanner integration testing. **Stack:** Python (bacpypes3, docker-compose), macvlan networking.

#### digital-twin
**DOPPEL** — FRCS digital twin of a small commercial HVAC plant (17,500 ft², 50-ton CW plant). Synthetic physics + BACnet/IP emulation with Flask/HTMX HMI for operator training and fault injection. Two mutually exclusive, live-switchable twin models: `office-building` and the `barracks-cep` campus (10 barracks + central energy plant). Also carries a full electrical distribution model with breaker trip logic and per-equipment sub-metering, black-start with motor inrush and standby generator/ATS, PI/PID supervisory control (CHWS reset, economizer, lead/lag), a Modbus/TCP server, a Niagara oBIX/REST-BQL emulation layer, 3D plant graphics, and a Niagara N4 Px generator. **Config-driven mode** emulates a specific real site from a Niagara Supervisor backup (`config.bog`) via the shared `niagara-config` library — publishing that site's real point names/topology over the Niagara surfaces, physics where modeled and a coverage dial elsewhere (opt-in via `TWIN_FROM_BACKUP` + `TWIN_ENABLE_NIAGARA`; default behavior unchanged). Recent revisions: **2.13** cross-scope cascade diagnosis across barracks + CEP, **2.14** an open-fdd parity port taking the office-building detector set from 54 to 65, and **2.15** backup **history replay** — `HistoryReplaySource` interpolates real Workbench-exported point histories over the bound points, either as watchable live playback or headless via `config replay-backup`. **Stack:** Python (BAC0, Flask, Click), BACnet/IP, Modbus/TCP, HTMX + Three.js. ~1,020 tests across 87 files. Ports 8080 (HMI), 8081/8082 (Niagara emulator).

#### niagara-llm
CASCADE — external analysis brain that monitors Niagara BAS stations (real-time point values + historical trends) via Niagara-faithful interfaces (oBIX, REST/BQL, SQL history export) behind a single `StationDataSource` abstraction, so it ports to a real JACE/Supervisor by config change. v2 runs fully air-gapped with a local LLM (Ollama), adaptive baselines, and RAG-grounded diagnosis; current work is closed-loop write-back, multi-station/fleet monitoring, and the operator dashboard. Also includes a Supervisor audit CLI (federation/architecture/security/platform-health analyzers) and a backup-assessment tool that replays a Supervisor backup's history through the detectors to produce a branded ROI/instrumentation-gap report. Its Supervisor-backup parser + semantic classifier were extracted (2026-07) into the shared `niagara-config` library, which niagara-llm now consumes via re-export shims. Developed against the digital-twin's Niagara emulation layer (the twin's FaultEngine is the test oracle). Its README keeps a deliberately evidence-qualified validation table — backup ingestion and native `.hdb` decoding are *backup-validated*, oBIX/BQL is *twin-validated*, one authorized Niagara 4.15 lab station is *live-validated* for lobby discovery plus a bounded 43-point read, while real histories/alarms/soak remain *pilot pending* and write-back stays *experimental*. **Stack:** Python (FastAPI, httpx, Ollama, Claude API), SQLite, Docker appliance bundle. Port 8770. ~960 tests across 110 files.

#### siem-forwarder
Niagara 4 JACE module that forwards security-relevant station events (point value/status changes and alarms) to a SIEM over RFC 5424 syslog/TLS, built around a non-interference design: ride-along subscriptions only (never adds polls to the RS-485 field bus), bounded drop-oldest queue drained by a below-normal-priority worker thread, and self-throttling with explicit gap events. It forwards **points + alarms only** — audit/platform logs are deliberately left to Niagara's own native remote syslog (4.10+), because reading audit records would require Tridium-internal `com.tridium.history.audit.*` APIs; `forwardAudit` survives as a config slot but is not acted on. Skeleton — structure, threading model, and safety patterns complete; bind points marked for the target Niagara build. **Stack:** Java (Niagara 4 module API, Gradle). Design doc: `~/dev/siem-forwarder/siemForwarder-SDD.docx` (plus `-AddendumA`) — the project lives in its own repo now, not under this tree.

#### pocket-probe
Keychain-sized network discovery device (codename *whats-your-name*) that captures LLDP/CDP frames to identify upstream switches, ports, VLANs, management IPs, capabilities, and PoE info, displaying them on a 1.8″ OLED with a QR handoff to a phone. Firmware works on an STM32F767 Nucleo dev board; v0 hardware is in early KiCad schematic capture, PCB layout not started. Renamed from `Pocket Probe` and re-homed to `github.com/ogreen111/pocket-probe` in 2026-08 after its original git history was found corrupted (working tree was intact; history was reinitialized). **Stack:** C (STM32F767 HAL), KiCad, Python simulators (Scapy).

#### prtg-import
PowerShell automation for bulk device deployment into PRTG network monitoring from CSV. Devices route into per-site groups by /24 prefix, get tagged with hardware metadata, and resume monitoring — all idempotently, with a dry-run mode. Renamed from `PRTG Import` in 2026-08 (its remote was already `PRTG-Import`); the same pass merged a long-diverged origin refactor back into local. **Stack:** PowerShell 5.1+, PRTG API.

#### kml
Utilities for generating KML files, Niagara network topology, and building centroids from JBLM commissioning data. **Stack:** JavaScript (KML generation), Python (JBLM parsing), CSV/xlsx.

---

### Platform / Shared

Shared libraries, design system, and infrastructure consumed by other projects.

#### cert-manager
Web app to manage employee training certificates. Parses certs via a multi-stage pipeline (regex filename → PDF text → Tesseract OCR → manual review queue), tracks expiry from explicit dates or per-cert-type TTLs, and syncs in real time with the shared folder via watchdog. React UI with invite-based auth, bulk archive/delete/assign, CSV export, and a person × cert-type matrix view. **Stack:** FastAPI + SQLAlchemy, React + Vite + TypeScript, SQLite, Tailwind + shadcn/ui, account-store. Ports 8002 (API) / 5173 (Vite). v0.0.1 — feature-rich but the thinnest test suite of any production-facing app here (7 tests).

#### account-store
Shared pip-installable Python library for local user account management (pbkdf2_sha256). Role-based access (admin/reviewer/viewer), JSON-backed storage, legacy migration. 26 tests. The portfolio's most widely shared dependency — consumed by eight projects: rfp-automation, project-tracking, email-processor, past-performance, project-monitor, cert-manager, project-creation, and digital-twin. Consumers wire it up five different ways (absolute path in `pyproject.toml`, editable install, a direct `site-packages` symlink, a bare `PYTHONPATH`, and a `tool.uv.sources` relative path) — none of which survive the library moving without a reinstall; see `CLAUDE.md` for the full re-pointing record.

#### niagara-config
Shared Python library for parsing Niagara Supervisor backups (`config.bog`) and classifying station points into an equipment/role semantic model. Extracted from niagara-llm (the `backup`/`semantic`/`model`/`topology`/`catalog`/`sources.base` cluster) to be a single source of truth consumed by both **niagara-llm** (via re-export shims, so its existing imports are unchanged) and the **digital-twin** (whose config-driven mode emulates a real site from a backup). **Stack:** Python (pydantic only), hatchling. 30 tests. Status: Library.

#### ssi-design-system
Single source of truth for SSi brand tokens (colors, typography, spacing, radii, shadows). CSS custom properties, Python brand.py, build + sync scripts. Now also home to the Niagara 4 engineering standard: point naming contract, point dictionary (xlsx), data-driven plant graphics rendered to PNG/Px/SVG, 10 standard Px view templates, kitPx artwork catalog, and a Px authoring guide. **v0.1.0**, Phases 1–3 complete; project-tracking is the v0 pilot. 49 tests. `apps.json` marks six consumers enabled (project-tracking, rfp-automation, email-processor, cyber-artifact-gen, digital-twin, floor-plan-editor). ⚠️ `sync.py` currently syncs to nobody: `apps.json`'s `_root` still points at the pre-migration `~/Documents/dev`, so every app resolves to a missing directory and gets skipped.

#### claude-sync
macOS daemon resolving Syncthing conflict files in `~/.claude/projects/` using per-glob merge strategies (3-way merge for memory, newest-mtime for regenerable files). Includes healthcheck + menu bar app. **Stack:** Python, Syncthing, launchd. 230 tests. Binds 127.0.0.1:8866.

#### claude-memory-compiler
Personal knowledge base compiled from Claude Code conversations: hook-based capture → daily logs → structured, cross-referenced knowledge articles with health checks (session → flush → compile → query → lint pipeline). No vector DB or RAG. Unusual among these projects in keeping its uv-managed venv entirely outside the project tree (via `bin/uvr.sh`), and in being wired into `~/.claude/settings.json`'s SessionStart/PreCompact/SessionEnd hooks rather than launched directly. **Stack:** Python 3.12+, Claude Agent SDK. Status: v0.

---

### Standalone Tools

#### sanguine
Internal Levels.com-style blood-lab results viewer with multi-person support: PDF/CSV + Apple Health import, optimal vs standard reference ranges (~50 biomarkers, sex-specific), trends, biomarker detail pages, PhenoAge biological age, Centenarian Decathlon goal tracking, Four Horsemen risk view, and Claude-generated cached explanations. Each OAuth-authenticated user gets their own auto-created person, panels, and trends; CSV is the robust import path, PDF parsing is best-effort and reports its recognition rate. **Stack:** Python (FastAPI, SQLite, PyMuPDF, pytesseract, Anthropic SDK). Port 8771. 130 tests.

#### scribe
SSI Scribe — self-hosted, privacy-first AI meeting note taker (split out of rfp-automation into its own repo: github.com/ogreen111/scribe). Bot-free browser capture with live transcript plus recording upload, Whisper/MLX transcription, pyannote speaker diarization, and Ollama-served gpt-oss:120b structured summaries (decisions, action items with owners, recap email draft). Cross-meeting Ask-AI with citations, FTS5 search, talk-time analytics, tags, and Word/Markdown/transcript exports. Also captures shared-screen frames during live recordings (OCR'd into search when tesseract is present) and embeds them in the Word export. **Stack:** Python (FastAPI, SQLite WAL+FTS5), vanilla-JS SPA, Whisper/MLX, pyannote, Ollama. Port 8736 (uvicorn terminates TLS directly). ~460 tests across 40 files.

#### floor-plan-editor
Single-file web app for editing 2D floor plans (from RoboRock vacuum maps), 3D dollhouse view, and Home Assistant picture-elements card export. **Stack:** HTML5 + JavaScript (Three.js), localStorage, SVG export.

> ⚠️ **Not present on this Mac (noticed 2026-08-06).** Every other registry
> entry resolves to a directory under `~/dev/`; this one resolves to nothing,
> and it appears in none of the documented migration batches. It's gitignored
> with zero tracked files, so this repo holds no copy to restore from. Check
> the Mac Studio and Time Machine before treating it as lost. Kept listed here
> because the registry is the portfolio's source of truth for what should
> exist — see `CLAUDE.md`.

---

### Reference

#### niagara-docs
Local cache of Niagara 4.10/4.15 runtime binaries (bin/lib/modules) plus a Supervisor backup, used as a development reference for the Niagara projects. Not an active codebase.

#### scripts
Mount automation scripts (sshfs to Ubuntu Docker + UDM Pro). Organizational container for future Bash utilities. Its own `og-scripts` repo at `~/dev/scripts` — not to be confused with this repo's untracked local tooling directory of the same name. **Stack:** Bash, watchdog scripts.

---

## Shared Architecture

```
account-store  ←─── rfp-automation
               ←─── project-tracking
               ←─── email-processor
               ←─── past-performance
               ←─── project-monitor
               ←─── cert-manager
               ←─── project-creation
               ←─── digital-twin (twin/auth.py)

rfp-automation ←─── project-creation (sibling path dependency)

ssi-design-system ←─── project-tracking (v0 pilot), rfp-automation, email-processor,
                       cyber-artifact-gen, digital-twin, floor-plan-editor
                       (⚠ apps.json _root still points at ~/Documents/dev — sync is a no-op)

virtual-devices ←─── network-scanner (integration tests)
digital-twin    ←─── niagara-llm (dev target: Niagara emulation layer + fault oracle)
                ←─── niagara-llm (labeled fixtures → diag-score offline scoring)

niagara-config  ←─── niagara-llm (backup parser + semantic classifier; via re-export shims)
                ←─── digital-twin (config-driven mode + backup history replay)
```

**Archived 2026-07-14:** cyber-proposals (removed), cyber-eac-tool (`_archive/cyber-eac-tool-20260711.tar.gz`), cyber-estimates (`_archive/cyber-estimates-20260714.tar.gz`). The NAVFAC/USACE cyber proposal and pricing logic is now packaged as the `navfac-cyber-proposal` Claude skill.

**Not in the registry, but present under `~/dev/`:** `sops`, `stream-deck` (a real, buildable Elgato Stream Deck plugin — the strongest candidate for promotion), and `trim-backup`, all untracked and gitignored; plus an empty `niagara-mcp-integration` directory.

See `DESIGN.docx` for the full architecture diagram and data-flow breakdown, and `PORTS.md` / `CLAUDE.md` for the portfolio port map.
