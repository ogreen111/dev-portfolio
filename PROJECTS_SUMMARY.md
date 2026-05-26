# Dev Folder Project Summary

A summary of all projects under `/Users/ogreen/Documents/dev/`, generated 2026-05-25.

---

## PRTG Import
**Purpose:** PowerShell automation for bulk device deployment into PRTG network monitoring using CSV files. Handles device creation, group routing, and tag application with safe re-run behavior.
**Stack:** PowerShell 5.1+, PRTG API.
**Notes:** CLI automation tool; production-ready for PRTG configuration workflows.

## Pocket Probe
**Purpose:** Keychain-sized network discovery device (STM32F767 firmware + KiCad hardware) that captures LLDP and CDP frames to identify upstream switches, VLANs, and management IPs on any Ethernet port.
**Stack:** C (STM32 HAL), KiCad, Python simulators (Scapy).
**Notes:** Early-stage hardware project; firmware works on Nucleo dev board; v0 PCB layout not yet started.

## account-store
**Purpose:** Shared Python package for local user account management with pbkdf2_sha256 password hashing. Extracted from rfp-automation; consumed by project-tracking and email-processor.
**Stack:** Python (pip-installable), JSON-backed storage, pbkdf2_sha256.
**Notes:** Reusable library with role-based access (admin/reviewer/viewer) and legacy migration.

## cert-manager
**Purpose:** Web app to manage employee training certificates in a shared folder. Parses certificate contents (filename + PDF text + OCR), tracks expiration, and serves a React UI for viewing/filtering.
**Stack:** FastAPI (Python backend), React + Vite + TypeScript, SQLite.
**Notes:** v0 read-only; Tailwind + shadcn/ui components; multi-stage name extraction pipeline planned.

## claude-sync
**Purpose:** macOS daemon that resolves Syncthing conflict files in `~/.claude/projects/` using per-glob merge strategies (3-way merge for memory files, newest-mtime for regenerable files).
**Stack:** Python, Syncthing, launchd agents, git merge-file.
**Notes:** Dual-Mac synchronization with health monitoring; includes healthcheck + menu bar app; 217-test suite.

## cyber-artifact-gen
**Purpose:** Converts Niagara BAS network exports to hardware/software diagrams and network schematics for DoD cyber proposals.
**Stack:** Python scripts, ad-hoc JSON/CSV processing.
**Notes:** Utility scripts for document generation; minimal documentation.

## cyber-eac-tool
**Purpose:** Browser-based calculator for earned-value forecasting on DoD cyber projects. Derives EAC, ETC, CPI, SPI, and risk-adjusted forecasts with Excel export.
**Stack:** JavaScript (frontend), Python (serve.py), openpyxl.
**Notes:** Standalone tool serving on localhost:8010; Sage Contractor integration for actuals import.

## cyber-estimates
**Purpose:** Builds DoD MILCON cybersecurity proposal artifacts (pricing workbooks + scope reviews) for solicitations referencing UFGS 25 05 11 and 25 08 11.
**Stack:** Python (openpyxl), Node.js (docx), templates + UFGS reference data.
**Notes:** Working directory for proposal generation; references the cyber-proposals skill.

## cyber-proposals
**Purpose:** Reusable DoD MILCON cybersecurity proposal toolkit for two USACE MATOCs (MRR + UMCS). Shared engine for pricing + scope extraction + tech proposal generation.
**Stack:** Python (Claude API, openpyxl), Node.js (docx), structured scope JSON, AI-driven extraction.
**Notes:** Multi-MATOC organization with per-MATOC pricing defaults and role codes; prompt caching enabled.

## digital-twin
**Purpose:** FRCS digital twin of a small commercial HVAC plant. Synthetic physics + BACnet/IP emulation with bundled Flask/HTMX HMI for operator training and fault-injection scenarios.
**Stack:** Python (BAC0, Flask, Click), BACnet/IP, dataclass-based physics.
**Notes:** 26 scenarios (23 faults + 3 cyber); 350+ tests; runs natively on ARM Macs; configurable time-compression.

## email-monitor
**Purpose:** Inbound email monitoring/processing component (placeholder portfolio item).
**Stack:** Unknown.
**Notes:** Project structure unclear; minimal visible implementation.

## email-processor
**Purpose:** Automated triage for inbound RFI/RFQ/RFP emails for SSI. Parses mail, fetches gated PWS/questions from GSA MRAS/SAM/eBuy/PIEE, summarizes via Claude, outputs to Obsidian vault + docx + webserver dashboard.
**Stack:** Python (uv, FastAPI, Playwright, Claude API), Obsidian output.
**Notes:** Production system; CMMC-compliant (no Graph API); dashboard with auth; multi-machine sync via OneDrive.

## ethernet-link-analyzer
**Purpose:** Passive Ethernet discovery tool for enterprise/government/OT networks. Identifies upstream switch, port, VLANs, voice VLAN, and management IPs from LLDP/CDP traffic. Raspberry Pi field-appliance target.
**Stack:** Python (scapy, libpcap, BPF), OUI lookup, rich (terminal), JSON export.
**Notes:** Phase 1 complete (LLDP/CDP/LLDP-MED parsing); passive-only constraint enforced.

## floor-plan-editor
**Purpose:** Single-file web app for editing 2D floor plans, viewing in 3D dollhouse, exporting Home Assistant picture-elements cards. Built from RoboRock vacuum maps.
**Stack:** HTML5 + JavaScript (Three.js), localStorage, SVG export.
**Notes:** Self-contained web app; coordinate system in inches; exports to HA cards.

## kml
**Purpose:** Utilities for parsing and generating KML files, Niagara network topology, and building centroids from JBLM (Joint Base Lewis-McChord) commissioning data.
**Stack:** JavaScript (KML generation), Python (JBLM parsing), CSV/xlsx input.
**Notes:** Utility collection for a specific site deployment.

## network-scanner
**Purpose:** Laptop-based network discovery and switch interrogation. Scans devices, ports, services; enumerates BACnet/IP; imports baselines from CSV/xlsx; provides web UI and CLI.
**Stack:** Python (nmap, netmiko, bacpypes3, FastAPI), SQLite, HTMX + Jinja templates.
**Notes:** v1 supports site-based scans with profiles; BACnet Who-Is + ReadProperty enumeration; 60+ tests; includes WPAFB BAS network simulator (76 devices).

## niagara-docs
**Purpose:** Documentation or reference materials for the Niagara BAS framework.
**Stack:** Unknown.
**Notes:** Appears to be a stub/placeholder with minimal visible implementation.

## outlook-followup
**Purpose:** Outlook email follow-up automation or task tracking (purpose inferred).
**Stack:** Unknown.
**Notes:** Project structure not clear from directory listing.

## past-performance
**Purpose:** Local web app that monitors a folder of SSI past-performance documents (PDF/DOCX/TXT/MD), full-text indexes with SQLite FTS5, and provides search + display + extraction + generation.
**Stack:** Python (FastAPI, SQLite FTS5, mammoth, pypdf, tesseract OCR), plain JS frontend.
**Notes:** v1 read/search only; Claude API for PP extraction/generation (stub); 34 tests.

## project-tracking
**Purpose:** Cross-references funding PDFs, labor PDFs, and Microsoft Planner exports to produce per-job dashboards covering budget, costs, labor hours, and submittal pipeline. FastAPI web portal with role-based auth.
**Stack:** Python (FastAPI, pdfplumber, openpyxl, mpxj), vanilla JS + Tabulator 5.5.
**Notes:** Multi-user with per-job ACL; snapshot history + diff; threshold alerts + Slack webhook; SSi design system integration.

## rfp-automation
**Purpose:** Automated extraction, analysis, and proposal generation for DoD/MILCON cybersecurity RFPs. Parses specs/drawings, classifies cyber governance (25 05 11 / 25 08 11), extracts scope, builds submittal matrices, generates drafts.
**Stack:** Python (PyMuPDF, python-docx, openpyxl, Playwright, Claude API), FastAPI dashboard.
**Notes:** Production system with 1800+ tests; dashboard at port 8108; cyber-proposals adapter hooks in.

## scripts
**Purpose:** Parent workspace for script-based projects and utilities. Currently contains mount automation (sshfs mounts to Ubuntu Docker + UDM Pro).
**Stack:** Bash shell scripts, watchdog scripts.
**Notes:** Organizational container with mounts/ folder for Ubuntu/UDM automation.

## ssi-design-system
**Purpose:** Single source of truth for SSi brand tokens (colors, typography, spacing, radii, shadows). Consumed by all SSi web + document-generation apps.
**Stack:** JSON tokens, CSS custom properties, Python brand.py, build/sync scripts.
**Notes:** v0.1.0 with Phases 1–3 complete; light/dark theme support; project-tracking is v0 pilot.

## virtual-devices
**Purpose:** Fleet of BACnet/IP "virtual buildings" that share a network with a real JACE 9000. Each container = one realistic building with behavior models, point lists, and multi-vendor identity.
**Stack:** Python (bacpypes3, docker-compose), macvlan networking, 5 archetypes.
**Notes:** Linux-only (macvlan requires bridged NIC); 76 devices total, 53 BACnet-bearing; smoke test runs offline on macOS.
