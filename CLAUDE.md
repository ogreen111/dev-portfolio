# Dev Portfolio — Claude Context

This directory (`~/Documents/dev/`) is the root of a personal development workspace containing 24 projects built around three core domains:

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
| email-monitor | Email monitoring component | Stub |
| outlook-followup | Outlook follow-up automation | Stub |
| past-performance | SSi past-performance doc search + extraction | v1 |
| project-tracking | Job budget/cost/labor/submittal dashboard | v1 |
| network-scanner | Active network discovery + BACnet enumeration | v1 |
| ethernet-link-analyzer | Passive LLDP/CDP Ethernet discovery | Phase 1 |
| virtual-devices | BACnet/IP virtual building fleet (76 devices) | v1 |
| digital-twin | FRCS HVAC plant digital twin + fault injection | v1 |
| Pocket Probe | STM32 LLDP/CDP keychain device | Prototype |
| PRTG Import | Bulk PRTG device import from CSV | Production |
| kml | KML/topology generation utilities (JBLM) | Utility |
| cert-manager | Employee training cert tracker | v0 |
| account-store | Shared user account management library | Library |
| ssi-design-system | SSi brand tokens + CSS + doc generation | v0.1 |
| claude-sync | Syncthing conflict resolver for ~/.claude | v1 |
| floor-plan-editor | 2D/3D floor plan editor → HA card export | Active |
| niagara-docs | Niagara BAS reference docs | Stub |
| scripts | Mount automation + Bash utilities | Active |

---

## Shared Dependencies

- **account-store** → consumed by: rfp-automation, project-tracking, email-processor
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

## Port Map

| Port | Project |
|---|---|
| 8010 | cyber-eac-tool |
| 8108 | rfp-automation dashboard |

---

## Key Files

- `README.md` — full project index with descriptions
- `PROJECTS_SUMMARY.md` — compact per-project summary (auto-generated)
- `DESIGN.docx` — portfolio architecture doc (data flows, shared libs, roadmap)
- `PROJECTS_SUMMARY.docx` — same content as PROJECTS_SUMMARY.md in Word format
