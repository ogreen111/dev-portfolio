# Dev Folder Project Summary

A summary of all projects under `/Users/ogreen/Documents/dev/`, generated 2026-07-04.

---

## PRTG Import
**Purpose:** PowerShell automation for bulk device deployment into PRTG network monitoring using CSV files. Handles device creation, group routing, and tag application with safe re-run behavior.
**Stack:** PowerShell 5.1+, PRTG API.
**Notes:** CLI automation tool; production-ready. Device IP address column added June 2026.

## Pocket Probe
**Purpose:** Keychain-sized network discovery device (STM32F767 firmware + KiCad hardware) that captures LLDP and CDP frames to identify upstream switches, VLANs, and management IPs on any Ethernet port.
**Stack:** C (STM32 HAL), KiCad, Python simulators (Scapy).
**Notes:** Early-stage hardware project; firmware works on Nucleo dev board; v0 PCB layout not yet started.

## account-store
**Purpose:** Shared Python package for local user account management with pbkdf2_sha256 password hashing. Extracted from rfp-automation.
**Stack:** Python (pip-installable), JSON-backed storage, pbkdf2_sha256.
**Notes:** Reusable library with role-based access (admin/reviewer/viewer) and legacy migration. Consumed by rfp-automation, project-tracking, email-processor, project-monitor.

## cert-manager
**Purpose:** Web app to manage employee training certificates in a shared folder. Parses certificate contents (filename + PDF text + OCR), tracks expiration, and serves a React UI for viewing/filtering.
**Stack:** FastAPI (Python backend), React + Vite + TypeScript, SQLite.
**Notes:** v0 with auth, OCR, bulk operations, and matrix view; Tailwind + shadcn/ui components. Ports 8002/5173.

## claude-memory-compiler
**Purpose:** Personal knowledge base that automatically compiles Claude Code conversations into searchable structured articles. Conversations are captured via hooks, flushed to daily logs, and compiled into cross-referenced knowledge articles with health checks.
**Stack:** Python 3.12+, Claude Agent SDK; no vector DB or RAG.
**Notes:** v0 prototype; session → flush → compile → query → lint pipeline; installed across 3 Macs via iCloud-synced tree.

## claude-sync
**Purpose:** macOS daemon that resolves Syncthing conflict files in `~/.claude/projects/` using per-glob merge strategies (3-way merge for memory files, newest-mtime for regenerable files).
**Stack:** Python, Syncthing, launchd agents, git merge-file.
**Notes:** Dual-Mac synchronization with health monitoring; includes healthcheck + menu bar app; 217-test suite. Structured logging + SQLite sink added June 2026.

## cyber-artifact-gen
**Purpose:** Converts Niagara BAS network exports to hardware/software diagrams and network schematics for DoD cyber proposals.
**Stack:** Python scripts, ad-hoc JSON/CSV processing.
**Notes:** Utility scripts for document generation; brand/a11y contrast updates June 2026.

## cyber-brain
**Purpose:** Knowledge management system for the SSi cyber & integration group. Ingests Microsoft Graph data (SharePoint, Planner, Teams transcripts, email) into a normalized per-project SQLite event stream with FTS5, then generates onboarding briefs, answers questions with citations, and produces digests.
**Stack:** Python 3.11+ (FastAPI, msal/Graph SDK, SQLite FTS5, extract-msg, PyPDF).
**Notes:** v0.1 prototype; CUI-aware handling; CSV ingestion added July 2026; 13 tests; web UI on port 8772.

## daily-summary
**Purpose:** Power Automate solution for an automated daily email digest, packaged as a Microsoft solution zip.
**Stack:** Power Automate (Microsoft cloud workflow engine).
**Notes:** v0; no development since May 2026.

## digital-twin
**Purpose:** FRCS digital twin of a small commercial HVAC plant (17,500 ft², 50-ton CW plant). Synthetic physics + BACnet/IP emulation with Flask/HTMX HMI for operator training and fault-injection scenarios.
**Stack:** Python (BAC0, Flask, Click), BACnet/IP, Modbus/TCP, HTMX + Three.js 3D graphics.
**Notes:** v1.12 with major 2026 expansion: selectable twin models (office-building / barracks-cep campus, mutually exclusive, live-switchable from the HMI), full electrical distribution model (breaker trip logic, sub-metering), PI/PID supervisory control, ~50-detector FDD engine + probabilistic diagnoser, Niagara oBIX/REST-BQL emulation layer, N4 Px generator. 2026-07: config-driven mode (via `niagara-config`) emulates a specific real site from a Niagara Supervisor backup — publishing real point names/topology, physics where modeled + a coverage dial elsewhere (opt-in via `TWIN_FROM_BACKUP` + `TWIN_ENABLE_NIAGARA`). Config-mode FDD validation adds a per-detector equipment/role catalog, a `config coverage` report (which detectors can run on a given site), fault injection addressed by real equipment id, findings named in real config terms, and `config export-fixtures` labeled diagnosis fixtures consumed by niagara-llm's scorer. 927 tests. Ports 8080/8081/8082.

## email-processor
**Purpose:** Automated triage for inbound RFI/RFQ/RFP emails for SSi. Parses mail, fetches gated PWS/questions from GSA MRAS/SAM/eBuy/PIEE, summarizes via Claude, outputs to Obsidian vault + docx + webserver dashboard.
**Stack:** Python (uv, FastAPI, Playwright, Claude API), Obsidian output.
**Notes:** Production system; CMMC-compliant (no Graph API); dashboard with auth (port 8765); multi-machine sync via OneDrive; v2 watcher + portal fetchers landed June 2026.

## ethernet-link-analyzer
**Purpose:** Passive Ethernet discovery tool for enterprise/government/OT networks. Identifies upstream switch, port, VLANs, voice VLAN, and management IPs from LLDP/CDP traffic. Raspberry Pi field appliance with touch UI, web HMI, and PiSugar battery management.
**Stack:** Python (Scapy, libpcap, BPF), OUI lookup, rich, JSON export; SPI touchscreen + WiFi AP mode on the appliance.
**Notes:** Phases 1–3 complete (protocol parsing, vendor fingerprinting, OT presence detection, field appliance); Phase 4 in progress (long-duration monitoring, ARP host inventory, baseline/drift anomaly detection). Operator-gated active-test mode (connectivity, PHY cable test, speed qualification), off by default. 137 tests.

## floor-plan-editor
**Purpose:** Single-file web app for editing 2D floor plans, viewing in 3D dollhouse, exporting Home Assistant picture-elements cards. Built from RoboRock vacuum maps.
**Stack:** HTML5 + JavaScript (Three.js), localStorage, SVG export.
**Notes:** Self-contained web app; coordinate system in inches; exports to HA cards.

## fulcrum-replacement
**Purpose:** In-house offline-first mobile field data collection platform (iOS/Android) to replace the ~$40k/yr Fulcrum subscription. Covers BAS asset surveys, JACE commissioning checklists, and QC inspections.
**Stack (proposed):** Capacitor (React/Vite mobile wrapper), FastAPI + PostGIS backend, durable offline SQLite.
**Notes:** Design stage only — design doc rev 4 (2026-07-02) with requirements, ROI analysis (~14–15 month payoff), and offline-durability risk spike. Proposed port 8773.

## kml
**Purpose:** Utilities for parsing and generating KML files, Niagara network topology, and building centroids from JBLM (Joint Base Lewis-McChord) commissioning data.
**Stack:** JavaScript (KML generation), Python (JBLM parsing), CSV/xlsx input.
**Notes:** Utility collection for a specific site deployment.

## network-scanner
**Purpose:** Laptop-based network discovery and switch interrogation. Scans devices, ports, services; enumerates BACnet/IP; imports baselines from CSV/xlsx; provides web UI and CLI.
**Stack:** Python (nmap, netmiko, bacpypes3, FastAPI), SQLite, HTMX + Jinja templates.
**Notes:** v1 with site-based scans + profiles; BACnet Who-Is + ReadProperty enumeration; field simulation and scan-run control added 2026; 60+ tests; includes WPAFB BAS network simulator (76 devices). Port 8000.

## niagara-config
**Purpose:** Shared Python library that parses Niagara Supervisor backups (`config.bog`) and classifies station points into an equipment/role semantic model. Extracted from niagara-llm to be a single source of truth for Niagara-backup handling.
**Stack:** Python (pydantic only), hatchling.
**Notes:** Library. Public API across `backup`/`semantic`/`model`/`topology`/`catalog`/`sources.base`. Consumed by niagara-llm (via re-export shims, so its existing imports are unchanged) and by digital-twin's config-driven mode. Its `semantic` `Role`/`EquipType` values are the canonical vocabulary both consumers bind to — digital-twin's FDD detector catalog validates its declared point roles against them. Created 2026-07.

## niagara-docs
**Purpose:** Local reference cache of Niagara 4.10/4.15 runtime binaries (bin/lib/modules) plus a Supervisor backup, used for developing the Niagara-facing projects.
**Stack:** — (binary cache, not a codebase).
**Notes:** Stub/reference only; no active development.

## niagara-llm
**Purpose:** CASCADE — external analysis brain that monitors Niagara BAS stations (real-time point values + historical trends) for issues via Niagara-faithful interfaces (oBIX, REST/BQL, SQL history export) behind a single `StationDataSource` abstraction; ports to a real JACE/Supervisor by config change.
**Stack:** Python (FastAPI, httpx, Ollama local LLM, Claude API), SQLite, Docker appliance bundle.
**Notes:** v2 — fully air-gapped local-LLM operation, adaptive baselines, RAG-grounded diagnosis; current phase is closed-loop write-back + fleet monitoring + operator dashboard. Includes Supervisor audit CLI (federation/architecture/security analyzers) and backup-assessment ROI reporting. The Supervisor-backup parser + semantic classifier were extracted (2026-07) into the shared `niagara-config` library, now consumed via re-export shims. Developed against digital-twin's Niagara emulation (FaultEngine as test oracle); a `diag-score` CLI + `FixtureSource` now grade detection offline against digital-twin's labeled diagnosis fixtures (JSON files are the decoupling contract — no live server needed). 48 test files. Port 8770.

## outlook-followup
**Purpose:** Outlook email follow-up automation or task tracking (purpose inferred).
**Stack:** Unknown.
**Notes:** Stub; minimal visible implementation.

## past-performance
**Purpose:** Local web app that monitors a folder of SSi past-performance documents (PDF/DOCX/TXT/MD), full-text indexes with SQLite FTS5, and provides search + display + extraction + generation.
**Stack:** Python (FastAPI, SQLite FTS5, mammoth, pypdf, tesseract OCR), plain JS frontend.
**Notes:** v1; Claude-assisted extraction/generation and semantic search added June 2026; 34 tests. Port 8767.

## project-monitor
**Purpose:** Monitors project document folders and Outlook email to maintain per-project entity registers (contracts, mods, ASIs, POs, invoices, pay applications, completion progress) using deterministic path classifiers + Claude extraction; rolls up into program status views (web dashboard, Word report, STATUS.md).
**Stack:** Python (FastAPI, SQLite, Microsoft Graph SDK, python-docx, openpyxl, extract-msg), account-store auth.
**Notes:** v2 register architecture (shipped in four waves, June 2026) with v1→v2 migration; 27 tests. Port 8769.

## project-tracking
**Purpose:** Cross-references funding PDFs, labor PDFs, and Microsoft Planner data to produce per-job dashboards covering budget, costs, labor hours, and submittal pipeline. FastAPI web portal with role-based auth.
**Stack:** Python (FastAPI, pdfplumber, openpyxl, mpxj), React 18 (Vite + TypeScript + Tailwind), account-store.
**Notes:** v1 with the React SPA (v2 UI) now primary. 2026 additions: Microsoft Graph Planner sync, SharePoint document sourcing, per-job completion-source picker, per-phase/CLIN breakdown + contract/billing rollup from Sage exports, per-job ACLs + sharing, auto-refresh on file change. 42 test files. Port 8768.

## rfp-automation
**Purpose:** Automated extraction, analysis, and proposal generation for DoD/MILCON cybersecurity RFPs. Parses specs/drawings, classifies cyber governance (25 05 11 / 25 08 11), extracts scope, builds submittal matrices, generates drafts.
**Stack:** Python (PyMuPDF, python-docx, openpyxl, Playwright, Claude API), FastAPI dashboard.
**Notes:** Production system, 1800+ tests, dashboard on port 8008. 2026 additions: email intake with PIID identity gate, bid follow-up tracking + Planner comments, amendment cyber review (local Ollama for CUI), redesigned dashboard with SSE live updates, per-project Ask-AI chat, SENTRY self-improvement loop (launchd), TCC-safe state dir at `~/Library/RFPAutomation/state/`.

## sanguine
**Purpose:** Internal Levels.com-style blood-lab results viewer with multi-person support: PDF/CSV + Apple Health import, optimal vs standard reference ranges (~50 biomarkers, sex-specific), trends, biomarker detail pages, and Claude-generated cached educational content.
**Stack:** Python (FastAPI, SQLite, PyMuPDF + PyPDF, pytesseract OCR, Anthropic SDK).
**Notes:** v1 (renamed from levels-labs, July 2026); PhenoAge biological age, HOMA-IR auto-computation, Centenarian Decathlon tracker, Four Horsemen risk view. 16 tests. Port 8771.

## scribe
**Purpose:** SSI Scribe — self-hosted, privacy-first AI meeting note taker (split out of rfp-automation into its own repo: github.com/ogreen111/scribe). Bot-free browser capture with live transcript plus recording upload, Whisper/MLX transcription, pyannote speaker diarization, and Ollama-served gpt-oss:120b structured summaries (decisions, action items with owners, recap email draft).
**Stack:** Python (FastAPI, SQLite WAL+FTS5), vanilla-JS SPA, Whisper/MLX, pyannote, Ollama.
**Notes:** v0.1; cross-meeting Ask-AI with citations, FTS5 search, talk-time analytics, tags, Word/Markdown/transcript exports. Port 8736.

## scripts
**Purpose:** Parent workspace for script-based projects and utilities. Currently contains mount automation (sshfs mounts to Ubuntu Docker + UDM Pro).
**Stack:** Bash shell scripts, watchdog scripts.
**Notes:** Organizational container with mounts/ folder for Ubuntu/UDM automation.

## siem-forwarder
**Purpose:** Niagara 4 JACE module forwarding security-relevant station events (point value/status changes, alarms, audit records) to a SIEM over RFC 5424 syslog/TLS with a non-interference design: ride-along subscriptions only, bounded drop-oldest queue, below-normal-priority worker, self-throttling with gap events.
**Stack:** Java (Niagara 4 module API, Gradle).
**Notes:** Skeleton/design-complete; call sites written against the Niagara 4.15.1 API surface; bind points remain for the target build (slot-o-matic, alarm/audit listener types, TLS trust store). 3 standalone unit tests. Design doc: `siemForwarder-SDD.docx`.

## ssi-design-system
**Purpose:** Single source of truth for SSi brand tokens (colors, typography, spacing, radii, shadows). Consumed by SSi web + document-generation apps. Also home to the Niagara 4 engineering standard.
**Stack:** JSON tokens, CSS custom properties, Python (brand.py, build/sync scripts, Niagara artifact builders), openpyxl + python-docx, Pillow.
**Notes:** v0.1.0, Phases 1–3 complete; project-tracking is the v0 pilot. Niagara workstream: point naming contract + point dictionary, data-driven plant graphics (PNG/Px/SVG), 10 Px view templates, kitPx artwork catalog, PX_AUTHORING guide. 9 test files.

## virtual-devices
**Purpose:** Fleet of BACnet/IP "virtual buildings" that share a network with a real JACE 9000. Each container = one realistic building with behavior models, point lists, and multi-vendor identity.
**Stack:** Python (bacpypes3, docker-compose), macvlan networking, 5 archetypes.
**Notes:** Linux-only (macvlan requires bridged NIC); 76 devices total, 53 BACnet-bearing; smoke test runs offline on macOS.
