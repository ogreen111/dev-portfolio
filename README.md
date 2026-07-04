# Dev Portfolio

Personal development workspace for tools and systems built around DoD/MILCON cybersecurity proposals, BAS/OT network engineering, and internal SSi productivity automation.

**32 projects** · Last updated 2026-07-04

---

## Quick Index

| Project | Category | Stack | Status |
|---|---|---|---|
| [rfp-automation](#rfp-automation) | Proposal Automation | Python, Claude API, FastAPI | Production |
| [cyber-proposals](#cyber-proposals) | Proposal Automation | Python, Claude API, Node.js | Production |
| [cyber-estimates](#cyber-estimates) | Proposal Automation | Python, Node.js | Active |
| [cyber-eac-tool](#cyber-eac-tool) | Proposal Automation | JS, Python | Active |
| [cyber-artifact-gen](#cyber-artifact-gen) | Proposal Automation | Python | Utility |
| [email-processor](#email-processor) | SSi Productivity | Python, FastAPI, Playwright | Production |
| [outlook-followup](#outlook-followup) | SSi Productivity | Unknown | Stub |
| [past-performance](#past-performance) | SSi Productivity | Python, FastAPI, SQLite | v1 |
| [project-tracking](#project-tracking) | SSi Productivity | Python, FastAPI, React | v1 |
| [project-monitor](#project-monitor) | SSi Productivity | Python, FastAPI, Graph SDK | v2 |
| [cyber-brain](#cyber-brain) | SSi Productivity | Python, FastAPI, Graph SDK | v0.1 |
| [daily-summary](#daily-summary) | SSi Productivity | Power Automate | v0 |
| [fulcrum-replacement](#fulcrum-replacement) | SSi Productivity | Capacitor, FastAPI, PostGIS | Design only |
| [network-scanner](#network-scanner) | Network / OT Tools | Python, FastAPI, nmap | v1 |
| [ethernet-link-analyzer](#ethernet-link-analyzer) | Network / OT Tools | Python, Scapy | Phase 4 |
| [virtual-devices](#virtual-devices) | Network / OT Tools | Python, bacpypes3, Docker | v1 |
| [digital-twin](#digital-twin) | Network / OT Tools | Python, BAC0, Flask | v1.10 |
| [niagara-llm](#niagara-llm) | Network / OT Tools | Python, FastAPI, Ollama, Claude API | v2 |
| [siem-forwarder](#siem-forwarder) | Network / OT Tools | Java (Niagara 4), Gradle | Skeleton/design-complete |
| [Pocket Probe](#pocket-probe) | Network / OT Tools | C, KiCad, Python | Prototype |
| [PRTG Import](#prtg-import) | Network / OT Tools | PowerShell | Production |
| [kml](#kml) | Network / OT Tools | JS, Python | Utility |
| [cert-manager](#cert-manager) | Platform / Shared | FastAPI, React, SQLite | v0 |
| [account-store](#account-store) | Platform / Shared | Python | Library |
| [ssi-design-system](#ssi-design-system) | Platform / Shared | JSON, CSS, Python | v0.1 |
| [claude-sync](#claude-sync) | Platform / Shared | Python, launchd | v1 |
| [claude-memory-compiler](#claude-memory-compiler) | Platform / Shared | Python, Claude Agent SDK | v0 |
| [floor-plan-editor](#floor-plan-editor) | Standalone Tools | HTML5, Three.js | Active |
| [sanguine](#sanguine) | Standalone Tools | Python, FastAPI, SQLite | v1 |
| [scribe](#scribe) | Standalone Tools | Python, FastAPI, Whisper/MLX, pyannote, Ollama | v0.1 |
| [niagara-docs](#niagara-docs) | Reference | — | Stub |
| [scripts](#scripts) | Reference | Bash | Active |

---

## Categories

### Proposal Automation

Tools that automate the full DoD/MILCON cybersecurity proposal lifecycle — from RFP intake through pricing, scope extraction, and tech proposal generation.

#### rfp-automation
Automated extraction, analysis, and proposal generation for DoD/MILCON cybersecurity RFPs. Parses specs and drawings, classifies cyber governance (UFGS 25 05 11 / 25 08 11), extracts scope, builds submittal matrices, and generates draft proposals. 2026 additions: email intake with PIID identity gate, bid follow-up tracking with Planner comment integration, amendment cyber review (local Ollama for CUI, cloud otherwise), redesigned dashboard with SSE live updates, per-project Ask-AI chat, and a launchd-driven SENTRY self-improvement loop. **Stack:** Python (PyMuPDF, python-docx, openpyxl, Playwright, Claude API), FastAPI dashboard (port 8008). 1800+ tests.

#### cyber-proposals
Reusable proposal engine shared across two USACE MATOCs (MRR + UMCS). Handles pricing, scope extraction, and tech proposal generation with per-MATOC defaults and prompt-cached Claude API calls. **Stack:** Python (Claude API, openpyxl), Node.js (docx).

#### cyber-estimates
Working directory for building individual DoD MILCON cybersecurity proposal artifacts — pricing workbooks and scope reviews for active solicitations. Consumes the cyber-proposals engine. **Stack:** Python (openpyxl), Node.js (docx).

#### cyber-eac-tool
Browser-based earned-value forecasting calculator for DoD cyber projects. Derives EAC, ETC, CPI, SPI, and risk-adjusted forecasts; exports to Excel. Sage Contractor integration for actuals import. **Stack:** JavaScript (frontend), Python (serve.py), openpyxl. Serves on localhost:8010.

#### cyber-artifact-gen
Converts Niagara BAS network exports to hardware/software diagrams and network schematics for use in DoD cyber proposals. **Stack:** Python scripts, JSON/CSV processing.

---

### SSi Productivity

Tools for email triage, document ingestion, past-performance tracking, project financial monitoring, and internal knowledge management.

#### email-processor
Automated triage for inbound RFI/RFQ/RFP emails at SSi. Parses mail, fetches gated documents from GSA MRAS/SAM/eBuy/PIEE portals, summarizes via Claude API, and outputs to Obsidian vault + docx + dashboard. CMMC-compliant (no Graph API). Syncs across machines via OneDrive. **Stack:** Python (uv, FastAPI, Playwright, Claude API). Port 8765.

#### outlook-followup
Outlook email follow-up automation or task tracking. **Stack:** Unknown. Status: stub.

#### past-performance
Local web app that monitors a folder of SSi past-performance documents (PDF/DOCX/TXT/MD), full-text indexes with SQLite FTS5, and provides search + display + Claude-assisted extraction and generation. **Stack:** Python (FastAPI, SQLite FTS5, mammoth, pypdf, tesseract OCR), plain JS frontend. Port 8767. 34 tests.

#### project-tracking
Cross-references funding PDFs, labor PDFs, and Microsoft Planner exports to produce per-job dashboards (budget, costs, labor hours, submittal pipeline). React SPA (v2 UI) is now the primary interface. 2026 additions: Microsoft Graph Planner sync (no manual exports), SharePoint document sourcing, per-job completion-source picker, per-phase/CLIN breakdown and contract/billing rollup from Sage exports, per-job ACLs + sharing. **Stack:** Python (FastAPI, pdfplumber, openpyxl, mpxj), React 18 (Vite + TypeScript + Tailwind), account-store auth. Port 8768. 42 test files.

#### project-monitor
Monitors project document folders and Outlook email to maintain per-project entity registers (contracts, mods, ASIs, POs, invoices, pay applications, completion progress) using deterministic path classifiers plus Claude extraction, then rolls up into program status views — web dashboard, Word report, and STATUS.md. v2 register architecture with v1→v2 migration. **Stack:** Python (FastAPI, SQLite, Microsoft Graph SDK, python-docx, extract-msg), account-store. Port 8769. 27 tests.

#### cyber-brain
Knowledge management system for the SSi cyber & integration group. Ingests Microsoft Graph data (SharePoint, Planner, Teams transcripts, email) into a normalized per-project SQLite event stream with FTS5, then generates onboarding briefs, answers questions with citations, and produces digests. CUI-aware handling. **Stack:** Python (FastAPI, msal/Graph SDK, SQLite FTS5, extract-msg, PyPDF). Port 8772. 13 tests.

#### daily-summary
Power Automate solution for an automated daily email digest, packaged as a Microsoft solution zip. **Stack:** Power Automate. Status: v0.

#### fulcrum-replacement
Design for an in-house, offline-first mobile field data collection platform (iOS/Android) to replace the ~$40k/yr Fulcrum subscription. Covers BAS asset surveys, JACE commissioning checklists, and QC inspections. **Stack (proposed):** Capacitor (React/Vite), FastAPI + PostGIS backend, durable offline SQLite. Design doc rev 4 (2026-07-02); no code yet. Proposed port 8773.

---

### Network / OT Tools

Tools for passive/active network discovery, BACnet simulation, and OT site engineering.

#### network-scanner
Laptop-based network discovery and switch interrogation. Scans devices, ports, and services; enumerates BACnet/IP; imports baselines from CSV/xlsx; provides web UI and CLI. Includes WPAFB BAS network simulator (76 devices across 5 archetypes) and field simulation / scan-run control. **Stack:** Python (nmap, netmiko, bacpypes3, FastAPI), SQLite, HTMX + Jinja. Port 8000. 60+ tests.

#### ethernet-link-analyzer
Passive Ethernet discovery for enterprise/government/OT networks. Identifies upstream switch, port, VLANs, voice VLAN, and management IPs from LLDP/CDP traffic. Phases 1–3 complete: protocol parsing (LLDP/LLDP-MED/CDP), vendor fingerprinting, multi-protocol OT presence detection, and a Raspberry Pi field appliance with touch UI, web HMI, and PiSugar battery management. Phase 4 in progress: long-duration monitoring, ARP-based host inventory, baseline/drift anomaly detection. Also includes an operator-gated active-test mode (connectivity, PHY cable test, link speed qualification) — off by default. **Stack:** Python (Scapy, libpcap, BPF), OUI lookup, rich, JSON export. 137 tests.

#### virtual-devices
Fleet of BACnet/IP virtual buildings that share a network with a real JACE 9000. 76 total devices (53 BACnet-bearing) across 5 archetypes (office/barracks/hangar/clinic/warehouse). Linux-only (macvlan). Used for network-scanner integration testing. **Stack:** Python (bacpypes3, docker-compose), macvlan networking.

#### digital-twin
FRCS digital twin of a small commercial HVAC plant (17,500 ft², 50-ton CW plant). Synthetic physics + BACnet/IP emulation with Flask/HTMX HMI for operator training and fault injection. Expanded substantially in 2026: campus multi-RTU mode (10 barracks + central energy plant), full electrical distribution model with breaker trip logic and per-equipment sub-metering, PI/PID supervisory control (CHWS reset, economizer, lead/lag), an FDD engine with ~50 detectors plus probabilistic diagnoser, Modbus/TCP server, Niagara oBIX/REST-BQL emulation layer, 3D plant graphics, and a Niagara N4 Px generator. **Stack:** Python (BAC0, Flask, Click), BACnet/IP, Modbus/TCP, HTMX + Three.js. 480+ tests. Ports 8080 (HMI), 8081/8082 (Niagara emulator).

#### niagara-llm
CASCADE — external analysis brain that monitors Niagara BAS stations (real-time point values + historical trends) via Niagara-faithful interfaces (oBIX, REST/BQL, SQL history export) behind a single `StationDataSource` abstraction, so it ports to a real JACE/Supervisor by config change. v2 runs fully air-gapped with a local LLM (Ollama), adaptive baselines, and RAG-grounded diagnosis; current work is closed-loop write-back, multi-station/fleet monitoring, and the operator dashboard. Also includes a Supervisor audit CLI (federation/architecture/security/platform-health analyzers) and a backup-assessment tool that replays a Supervisor backup's history through the detectors to produce a branded ROI/instrumentation-gap report. Developed against the digital-twin's Niagara emulation layer (the twin's FaultEngine is the test oracle). **Stack:** Python (FastAPI, httpx, Ollama, Claude API), SQLite, Docker appliance bundle. Port 8770. 47 test files.

#### siem-forwarder
Niagara 4 JACE module that forwards security-relevant station events (point value/status changes, alarms, audit records) to a SIEM over RFC 5424 syslog/TLS, built around a non-interference design: ride-along subscriptions only (never adds polls to the RS-485 field bus), bounded drop-oldest queue drained by a below-normal-priority worker thread, and self-throttling with explicit gap events. Skeleton — structure, threading model, and safety patterns complete; bind points marked for the target Niagara build. **Stack:** Java (Niagara 4 module API, Gradle). Design doc: `siem-forwarder/siemForwarder-SDD.docx`.

#### Pocket Probe
Keychain-sized network discovery device that captures LLDP/CDP frames to identify upstream switches, VLANs, and management IPs on any port. Firmware works on Nucleo dev board; v0 PCB layout not yet started. **Stack:** C (STM32F767 HAL), KiCad, Python simulators (Scapy).

#### PRTG Import
PowerShell automation for bulk device deployment into PRTG network monitoring from CSV. Safe re-run, group routing, tag application. **Stack:** PowerShell 5.1+, PRTG API.

#### kml
Utilities for generating KML files, Niagara network topology, and building centroids from JBLM commissioning data. **Stack:** JavaScript (KML generation), Python (JBLM parsing), CSV/xlsx.

---

### Platform / Shared

Shared libraries, design system, and infrastructure consumed by other projects.

#### cert-manager
Web app to manage employee training certificates. Parses certs (filename + PDF + OCR), tracks expiration; React UI with auth, bulk operations, and matrix view. **Stack:** FastAPI, React + Vite + TypeScript, SQLite, Tailwind + shadcn/ui. Ports 8002 (API) / 5173 (Vite).

#### account-store
Shared pip-installable Python library for local user account management (pbkdf2_sha256). Role-based access (admin/reviewer/viewer), JSON-backed storage, legacy migration. Consumed by rfp-automation, project-tracking, email-processor, project-monitor.

#### ssi-design-system
Single source of truth for SSi brand tokens (colors, typography, spacing, radii, shadows). CSS custom properties, Python brand.py, build + sync scripts. Now also home to the Niagara 4 engineering standard: point naming contract, point dictionary (xlsx), data-driven plant graphics rendered to PNG/Px/SVG, 10 standard Px view templates, kitPx artwork catalog, and a Px authoring guide. **v0.1.0**, Phases 1–3 complete; project-tracking is the v0 pilot.

#### claude-sync
macOS daemon resolving Syncthing conflict files in `~/.claude/projects/` using per-glob merge strategies (3-way merge for memory, newest-mtime for regenerable files). Includes healthcheck + menu bar app. **Stack:** Python, Syncthing, launchd. 217 tests.

#### claude-memory-compiler
Personal knowledge base compiled from Claude Code conversations: hook-based capture → daily logs → structured, cross-referenced knowledge articles with health checks (session → flush → compile → query → lint pipeline). No vector DB or RAG. **Stack:** Python 3.12+, Claude Agent SDK. Status: v0.

---

### Standalone Tools

#### floor-plan-editor
Single-file web app for editing 2D floor plans (from RoboRock vacuum maps), 3D dollhouse view, and Home Assistant picture-elements card export. **Stack:** HTML5 + JavaScript (Three.js), localStorage, SVG export.

#### sanguine
Internal Levels.com-style blood-lab results viewer with multi-person support: PDF/CSV + Apple Health import, optimal vs standard reference ranges (~50 biomarkers, sex-specific), trends, biomarker detail pages, PhenoAge biological age, Centenarian Decathlon goal tracking, Four Horsemen risk view, and Claude-generated cached explanations. **Stack:** Python (FastAPI, SQLite, PyMuPDF, pytesseract, Anthropic SDK). Port 8771. 16 tests.

#### scribe
SSI Scribe — self-hosted, privacy-first AI meeting note taker (split out of rfp-automation into its own repo: github.com/ogreen111/scribe). Bot-free browser capture with live transcript plus recording upload, Whisper/MLX transcription, pyannote speaker diarization, and Ollama-served gpt-oss:120b structured summaries (decisions, action items with owners, recap email draft). Cross-meeting Ask-AI with citations, FTS5 search, talk-time analytics, tags, and Word/Markdown/transcript exports. **Stack:** Python (FastAPI, SQLite WAL+FTS5), vanilla-JS SPA, Whisper/MLX, pyannote, Ollama. Port 8736.

---

### Reference

#### niagara-docs
Local cache of Niagara 4.10/4.15 runtime binaries (bin/lib/modules) plus a Supervisor backup, used as a development reference for the Niagara projects. Not an active codebase.

#### scripts
Mount automation scripts (sshfs to Ubuntu Docker + UDM Pro). Organizational container for future Bash utilities. **Stack:** Bash, watchdog scripts.

---

## Shared Architecture

```
account-store  ←─── rfp-automation
               ←─── project-tracking
               ←─── email-processor
               ←─── project-monitor

ssi-design-system ←─── project-tracking
                  ←─── (all SSi web apps)

cyber-proposals ←─── cyber-estimates
                ←─── rfp-automation (adapter)

virtual-devices ←─── network-scanner (integration tests)
digital-twin    ←─── niagara-llm (dev target: Niagara emulation layer + fault oracle)
```

See `DESIGN.docx` for the full architecture diagram and data-flow breakdown, and `PORTS.md` / `CLAUDE.md` for the portfolio port map.
