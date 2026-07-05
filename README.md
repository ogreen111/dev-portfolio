# Dev Portfolio

Personal development workspace for tools and systems built around DoD/MILCON cybersecurity proposals, BAS/OT network engineering, and internal SSi productivity automation.

**24 projects** · Last updated 2026-05-25

---

## Quick Index

| Project | Category | Stack | Status |
|---|---|---|---|
| [rfp-automation](#rfp-automation) | Proposal Automation | Python, Claude API, FastAPI | Production |
| [cyber-proposals](#cyber-proposals) | Proposal Automation | Python, Claude API, Node.js | Production |
| [cyber-estimates](#cyber-estimates) | Proposal Automation | Python, Node.js | Active |
| [cyber-eac-tool](#cyber-eac-tool) | Proposal Automation | JS, Python | Active |
| [cyber-artifact-gen](#cyber-artifact-gen) | Proposal Automation | Python | Utility |
| [email-processor](#email-processor) | Document Automation | Python, FastAPI, Playwright | Production |
| [email-monitor](#email-monitor) | Document Automation | Python | Stub |
| [outlook-followup](#outlook-followup) | Document Automation | Unknown | Stub |
| [past-performance](#past-performance) | Document Automation | Python, FastAPI, SQLite | v1 |
| [project-tracking](#project-tracking) | Document Automation | Python, FastAPI, Tabulator | v1 |
| [network-scanner](#network-scanner) | Network / OT Tools | Python, FastAPI, nmap | v1 |
| [ethernet-link-analyzer](#ethernet-link-analyzer) | Network / OT Tools | Python, Scapy | Phase 1 |
| [virtual-devices](#virtual-devices) | Network / OT Tools | Python, bacpypes3, Docker | v1 |
| [digital-twin](#digital-twin) | Network / OT Tools | Python, BAC0, Flask | v1 |
| [niagara-llm](#niagara-llm) | Network / OT Tools | Python, FastAPI, httpx, Claude API | v1 |
| [siem-forwarder](#siem-forwarder) | Network / OT Tools | Java (Niagara 4), Gradle | Skeleton/design-complete |
| [Pocket Probe](#pocket-probe) | Network / OT Tools | C, KiCad, Python | Prototype |
| [PRTG Import](#prtg-import) | Network / OT Tools | PowerShell | Production |
| [kml](#kml) | Network / OT Tools | JS, Python | Utility |
| [cert-manager](#cert-manager) | Platform / Shared | FastAPI, React, SQLite | v0 |
| [account-store](#account-store) | Platform / Shared | Python | Library |
| [ssi-design-system](#ssi-design-system) | Platform / Shared | JSON, CSS, Python | v0.1 |
| [claude-sync](#claude-sync) | Platform / Shared | Python, launchd | v1 |
| [floor-plan-editor](#floor-plan-editor) | Standalone Tools | HTML5, Three.js | Active |
| [scribe](#scribe) | Standalone Tools | Python, FastAPI, Whisper/MLX, pyannote, Ollama | v0.1 |
| [niagara-docs](#niagara-docs) | Reference | — | Stub |
| [scripts](#scripts) | Reference | Bash | Active |

---

## Categories

### Proposal Automation

Tools that automate the full DoD/MILCON cybersecurity proposal lifecycle — from RFP intake through pricing, scope extraction, and tech proposal generation.

#### rfp-automation
Automated extraction, analysis, and proposal generation for DoD/MILCON cybersecurity RFPs. Parses specs and drawings, classifies cyber governance (UFGS 25 05 11 / 25 08 11), extracts scope, builds submittal matrices, and generates draft proposals. **Stack:** Python (PyMuPDF, python-docx, openpyxl, Playwright, Claude API), FastAPI dashboard (port 8108). 1800+ tests.

#### cyber-proposals
Reusable proposal engine shared across two USACE MATOCs (MRR + UMCS). Handles pricing, scope extraction, and tech proposal generation with per-MATOC defaults and prompt-cached Claude API calls. **Stack:** Python (Claude API, openpyxl), Node.js (docx).

#### cyber-estimates
Working directory for building individual DoD MILCON cybersecurity proposal artifacts — pricing workbooks and scope reviews for active solicitations. Consumes the cyber-proposals engine. **Stack:** Python (openpyxl), Node.js (docx).

#### cyber-eac-tool
Browser-based earned-value forecasting calculator for DoD cyber projects. Derives EAC, ETC, CPI, SPI, and risk-adjusted forecasts; exports to Excel. Sage Contractor integration for actuals import. **Stack:** JavaScript (frontend), Python (serve.py), openpyxl. Serves on localhost:8010.

#### cyber-artifact-gen
Converts Niagara BAS network exports to hardware/software diagrams and network schematics for use in DoD cyber proposals. **Stack:** Python scripts, JSON/CSV processing.

---

### Document Automation

Tools for email triage, document ingestion, past-performance tracking, and project financial monitoring.

#### email-processor
Automated triage for inbound RFI/RFQ/RFP emails at SSi. Parses mail, fetches gated documents from GSA MRAS/SAM/eBuy/PIEE portals, summarizes via Claude API, and outputs to Obsidian vault + docx + dashboard. CMMC-compliant (no Graph API). Syncs across machines via OneDrive. **Stack:** Python (uv, FastAPI, Playwright, Claude API).

#### email-monitor
Inbound email monitoring component. **Stack:** Unknown. Status: stub.

#### outlook-followup
Outlook email follow-up automation or task tracking. **Stack:** Unknown. Status: stub.

#### past-performance
Local web app that monitors a folder of SSi past-performance documents (PDF/DOCX/TXT/MD), full-text indexes with SQLite FTS5, and provides search + display + Claude-assisted extraction and generation. **Stack:** Python (FastAPI, SQLite FTS5, mammoth, pypdf, tesseract OCR), plain JS frontend. 34 tests.

#### project-tracking
Cross-references funding PDFs, labor PDFs, and Microsoft Planner exports to produce per-job dashboards (budget, costs, labor hours, submittal pipeline). Role-based auth, snapshot history, Slack webhook alerts, SSi design system integration. **Stack:** Python (FastAPI, pdfplumber, openpyxl, mpxj), vanilla JS + Tabulator 5.5.

---

### Network / OT Tools

Tools for passive/active network discovery, BACnet simulation, and OT site engineering.

#### network-scanner
Laptop-based network discovery and switch interrogation. Scans devices, ports, and services; enumerates BACnet/IP; imports baselines from CSV/xlsx; provides web UI and CLI. Includes WPAFB BAS network simulator (76 devices across 5 archetypes). **Stack:** Python (nmap, netmiko, bacpypes3, FastAPI), SQLite, HTMX + Jinja. 60+ tests.

#### ethernet-link-analyzer
Passive Ethernet discovery for enterprise/government/OT networks. Identifies upstream switch, port, VLANs, voice VLAN, and management IPs from LLDP/CDP traffic. Raspberry Pi field-appliance target. Phase 1 complete. **Stack:** Python (Scapy, libpcap, BPF), OUI lookup, rich, JSON export.

#### virtual-devices
Fleet of BACnet/IP virtual buildings that share a network with a real JACE 9000. 76 total devices (53 BACnet-bearing) across 5 archetypes (office/barracks/hangar/clinic/warehouse). Linux-only (macvlan). Used for network-scanner integration testing. **Stack:** Python (bacpypes3, docker-compose), macvlan networking.

#### digital-twin
FRCS digital twin of a small commercial HVAC plant. Synthetic physics + BACnet/IP emulation with Flask/HTMX HMI for operator training and fault-injection. 26 scenarios (23 faults + 3 cyber), configurable time-compression. **Stack:** Python (BAC0, Flask, Click), BACnet/IP. 350+ tests.

#### niagara-llm
External analysis brain that monitors a Niagara BAS station — real-time point values and historical trend database — for issues. Consumes only Niagara-faithful interfaces (oBIX, REST/BQL, SQL history export) behind a single `StationDataSource` abstraction, so it ports to a real JACE/Supervisor by config change. v1 does rules + statistical FDD (10 seeded detectors) with Claude diagnosis-on-fire; developed against the digital-twin's Niagara emulation layer (the twin's FaultEngine is the test oracle). **Stack:** Python (FastAPI, httpx, Claude API), SQLite. 30 unit tests + live integration oracle. Design docs: `niagara-llm/docs/DESIGN.docx` / `.pdf`.

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
Web app to manage employee training certificates. Parses certs (filename + PDF + OCR), tracks expiration, React UI for viewing/filtering. **Stack:** FastAPI, React + Vite + TypeScript, SQLite, Tailwind + shadcn/ui.

#### account-store
Shared pip-installable Python library for local user account management (pbkdf2_sha256). Role-based access (admin/reviewer/viewer), JSON-backed storage, legacy migration. Consumed by rfp-automation, project-tracking, email-processor.

#### ssi-design-system
Single source of truth for SSi brand tokens (colors, typography, spacing, radii, shadows). CSS custom properties, Python brand.py, build + sync scripts. project-tracking is the v0 pilot. **v0.1.0**, Phases 1–3 complete.

#### claude-sync
macOS daemon resolving Syncthing conflict files in `~/.claude/projects/` using per-glob merge strategies (3-way merge for memory, newest-mtime for regenerable files). Includes healthcheck + menu bar app. **Stack:** Python, Syncthing, launchd. 217 tests.

---

### Standalone Tools

#### floor-plan-editor
Single-file web app for editing 2D floor plans (from RoboRock vacuum maps), 3D dollhouse view, and Home Assistant picture-elements card export. **Stack:** HTML5 + JavaScript (Three.js), localStorage, SVG export.

#### scribe
SSI Scribe — self-hosted, privacy-first AI meeting note taker (split out of rfp-automation into its own repo: github.com/ogreen111/scribe). Bot-free browser capture with live transcript plus recording upload, Whisper/MLX transcription, pyannote speaker diarization, and Ollama-served gpt-oss:120b structured summaries (decisions, action items with owners, recap email draft). Cross-meeting Ask-AI with citations, FTS5 search, talk-time analytics, tags, and Word/Markdown/transcript exports. **Stack:** Python (FastAPI, SQLite WAL+FTS5), vanilla-JS SPA, Whisper/MLX, pyannote, Ollama. Port 8736.

---

### Reference

#### niagara-docs
Documentation and reference materials for the Niagara BAS framework. Stub/placeholder.

#### scripts
Mount automation scripts (sshfs to Ubuntu Docker + UDM Pro). Organizational container for future Bash utilities. **Stack:** Bash, watchdog scripts.

---

## Shared Architecture

```
account-store  ←─── rfp-automation
               ←─── project-tracking
               ←─── email-processor

ssi-design-system ←─── project-tracking
                  ←─── (all SSi web apps)

cyber-proposals ←─── cyber-estimates
                ←─── rfp-automation (adapter)

virtual-devices ←─── network-scanner (integration tests)
digital-twin    ←─── (standalone BACnet test target)
```

See `DESIGN.docx` for the full architecture diagram and data-flow breakdown.
