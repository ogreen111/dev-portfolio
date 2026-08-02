# Dev Portfolio — Claude Context

This directory (`~/Documents/dev/`) is the root of a personal development workspace containing 30 projects built around three core domains:

1. **DoD/MILCON cybersecurity proposal automation** — RFP intake → pricing → tech proposal → EAC tracking
2. **BAS/OT network engineering** — passive discovery, BACnet simulation, site scanning, hardware prototypes
3. **SSi internal productivity** — email triage, project financial tracking, past-performance management

---

## Project Registry

Full per-project index: [README.md](README.md). Compact auto-generated
summary: [PROJECTS_SUMMARY.md](PROJECTS_SUMMARY.md). Read one of those for
project descriptions/status rather than duplicating them here.

---

## Shared Dependencies

- **account-store** → consumed by: rfp-automation, project-tracking, email-processor, project-monitor, cert-manager, project-creation
- **ssi-design-system** → consumed by: project-tracking, (planned for all SSi web apps)
- **virtual-devices** → used by: network-scanner for integration testing
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
  `.venv/bin/...` commands (e.g. the start commands in [PORTS.md](PORTS.md)) keep working.
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

Full reserved-port table + start commands: [PORTS.md](PORTS.md) (each app
binds its assigned port on startup; do not double-book). Two gotchas worth
keeping in mind without opening that file: **avoid port 8766** (silently
reserved at the OS level on this machine, no `lsof`-visible owner), and the
`claude-sync` daemon binds `127.0.0.1:8866`.

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
