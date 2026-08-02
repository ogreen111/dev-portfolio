# Port Reservations

Reserved ports for the dev portfolio. Each app binds its assigned port on startup; do not double-book.

| Port | Project | Service | Start command |
|---|---|---|---|
| 8000 | network-scanner | FastAPI backend | `cd network-scanner && .venv/bin/uvicorn scanner.app:app --host 0.0.0.0 --port 8000` |
| 8002 | cert-manager | FastAPI backend | `cd cert-manager/backend && .venv/bin/uvicorn app.main:app --port 8002` |
| 8008 | rfp-automation | dashboard (stdlib HTTP) | `cd rfp-automation && .venv/bin/rfp-auto dashboard` (reads `RFP_DASHBOARD_PORT` from `.env`) |
| 8080 | digital-twin | Flask HMI | `cd digital-twin/frcs-digital-twin && WEB_HMI_PORT=8080 .venv/bin/python -m twin.cli run` |
| 8081 | digital-twin | Niagara oBIX server (emulator) | `cd digital-twin/frcs-digital-twin && TWIN_ENABLE_NIAGARA=1 .venv/bin/python -m twin.cli run` (gated by `TWIN_ENABLE_NIAGARA=1`) |
| 8082 | digital-twin | Niagara REST/BQL endpoint (emulator) | same process as oBIX above (`NIAGARA_BQL_PORT`) |
| 8736 | scribe | Direct TLS (uvicorn), no reverse proxy — Traefik was retired | `launchctl kickstart -k gui/$(id -u)/com.ssi.scribe` (mkcert cert, binds 0.0.0.0) |
| 8737 | dev-portfolio | Plain HTTP (`ThreadingHTTPServer`), no TLS, per the **installed** `~/Library/LaunchAgents/com.ssi.portfolio.plist` — it sets `PORTFOLIO_SSL_CERTFILE`/`KEYFILE`, but `portfolio_server.py` never reads them, so those env vars are inert | `launchctl kickstart -k gui/$(id -u)/com.ssi.portfolio` (binds 0.0.0.0) |
| 8765 | email-processor | FastAPI + uvicorn | `cd email-processor && uv run email-intake serve` |
| 8767 | past-performance | FastAPI + uvicorn | `cd past-performance && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8767` |
| 8768 | project-tracking | FastAPI + uvicorn | `cd project-tracking && PT_PORT=8768 .venv/bin/python -m webapp` |
| 8769 | project-monitor | FastAPI + uvicorn | `cd project-monitor && PM_PORT=8769 .venv/bin/project-monitor run` |
| 8770 | niagara-llm | FastAPI + dashboard | `cd niagara-llm && uv run niagara-llm run` |
| 8771 | sanguine | FastAPI + dashboard | `cd sanguine && uv run sanguine run` (reads `SANGUINE_PORT`) |
| 8772 | cyber-brain | FastAPI + dashboard | `cd cyber-brain && uv run cyber-brain run` (reads `CB_HOST`/`CB_PORT`; binds 127.0.0.1 by default) |
| 8773 | project-creation | FastAPI (default `PROJECT_CREATION_PORT`) | reserved — `project_creation.app:create_app()` exists but the CLI (`project-creation`) is still a stub with no `run`/uvicorn wiring yet |
| 8774 | fulcrum-replacement | FastAPI + offline-first mobile app (planned) | reserved only — `fulcrum-replacement/` has no `pyproject.toml` or app code yet, just `DESIGN.md`/`DESIGN.docx`; no start command exists until it's built |
| 5173 | cert-manager | Vite frontend (proxies `/api` → 8002) | `cd cert-manager/frontend && npm run dev` |

## Notes

- past-performance, project-tracking, and email-processor all default to 8765 in their own READMEs; the portfolio-wide assignment moves them apart so they can run simultaneously.
- cert-manager's Vite proxy target in `frontend/vite.config.ts` must match the backend port (currently `8002`).
- **Avoid port 8766** — silently reserved at the OS level on this machine (visible via `netstat` as LISTEN on `127.0.0.1:8766` but with no `lsof`-visible owner).
- The `claude-sync` daemon binds `127.0.0.1:8866` (not a portfolio app server, but reserves the port).
- **Port 8010 (cyber-eac-tool) is intentionally absent**, not an oversight: cyber-eac-tool was archived 2026-07-14 (see `CLAUDE.md`'s Shared Dependencies note) and nothing live binds 8010 today. Its LaunchAgent (`com.ssi.cyber-eac-tool`) is still registered, though, and crash-loops every 30s because its working directory no longer exists — `launchctl bootout gui/$(id -u)/com.ssi.cyber-eac-tool` before reusing this port. `AGENTS.md`'s port table still lists it as if it were live and needs the same update.
- **`deploy/com.ssi.portfolio.plist` now matches the installed copy** — synced 2026-08-02 to the direct `0.0.0.0:8737` bind, the `~/dev/portfolio_server.py` script path, and the (currently inert) `PORTFOLIO_SSL_CERTFILE`/`KEYFILE` vars, replacing the stale pre-2026-07-05 Traefik-fronted description.

## Verification

Both commands below cover only ports that are up by default. Excluded:
8081/8082 (digital-twin's Niagara emulator, off unless `TWIN_ENABLE_NIAGARA=1`
— add them back when testing with that flag set), 8773 (project-creation,
CLI has no run/uvicorn wiring yet), and 8774 (fulcrum-replacement, nothing
to bind yet).

Roll-call command to confirm everything is bound:

```bash
lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk '$9 ~ /:(8000|8002|8008|8080|8736|8737|8765|8767|8768|8769|8770|8771|8772|5173)$/ {print $9, "->", $1, "(PID", $2")"}' | sort -u
```

HTTP probe (expect 200/302/303/401/404 — anything but "Connection refused"). Plain-HTTP
loopback services only — 8736 (scribe) genuinely terminates TLS (its `uvicorn.run` gets
`ssl_certfile`/`ssl_keyfile`), so probe it with
`curl -sk -o /dev/null -w '%{http_code}\n' https://127.0.0.1:8736/` instead (plain HTTP
against a TLS-only port fails the handshake and misreports as down). 8737 is genuinely
plain HTTP despite its plist's SSL env vars, so it stays in this loop:

```bash
for p in 8000 8002 8008 8080 8737 8765 8767 8768 8769 8770 8771 8772 5173; do
  echo "$p: $(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:$p/)"
done
```
