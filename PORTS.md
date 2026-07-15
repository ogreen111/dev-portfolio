# Port Reservations

Reserved ports for the dev portfolio. Each app binds its assigned port on startup; do not double-book.

| Port | Project | Service | Start command |
|---|---|---|---|
| 8000 | network-scanner | FastAPI backend | `cd network-scanner && .venv/bin/uvicorn scanner.app:app --host 0.0.0.0 --port 8000` |
| 8002 | cert-manager | FastAPI backend | `cd cert-manager/backend && .venv/bin/uvicorn app.main:app --port 8002` |
| 8008 | rfp-automation | dashboard (stdlib HTTP) | `cd rfp-automation && .venv/bin/rfp-auto dashboard` (reads `RFP_DASHBOARD_PORT` from `.env`) |
| 8080 | digital-twin | Flask HMI | `cd digital-twin/frcs-digital-twin && WEB_HMI_PORT=8080 .venv/bin/python -m twin.cli run` |
| 8737 | dev-portfolio | Traefik TLS → portfolio index/doc server on 127.0.0.1:18737 | LaunchAgents `com.ssi.traefik` + `com.ssi.portfolio` (https://host:8737) |
| 8765 | email-processor | FastAPI + uvicorn | `cd email-processor && uv run email-intake serve` |
| 8767 | past-performance | FastAPI + uvicorn | `cd past-performance && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8767` |
| 8768 | project-tracking | FastAPI + uvicorn | `cd project-tracking && PT_PORT=8768 .venv/bin/python -m webapp` |
| 8769 | project-monitor | FastAPI + uvicorn | `cd project-monitor && PM_PORT=8769 .venv/bin/project-monitor run` |
| 5173 | cert-manager | Vite frontend (proxies `/api` → 8002) | `cd cert-manager/frontend && npm run dev` |

## Notes

- past-performance, project-tracking, and email-processor all default to 8765 in their own READMEs; the portfolio-wide assignment moves them apart so they can run simultaneously.
- cert-manager's Vite proxy target in `frontend/vite.config.ts` must match the backend port (currently `8002`).
- **Avoid port 8766** — silently reserved at the OS level on this machine (visible via `netstat` as LISTEN on `127.0.0.1:8766` but with no `lsof`-visible owner).
- The `claude-sync` daemon binds `127.0.0.1:8866` (not a portfolio app server, but reserves the port).

## Verification

Roll-call command to confirm everything is bound:

```bash
lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | awk '$9 ~ /:(8000|8002|8008|8010|8080|8765|8767|8768|8769|5173)$/ {print $9, "->", $1, "(PID", $2")"}' | sort -u
```

HTTP probe (expect 200/302/303/401/404 — anything but "Connection refused"):

```bash
for p in 8000 8002 8008 8010 8080 8765 8767 8768 8769 5173; do
  echo "$p: $(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:$p/)"
done
```
