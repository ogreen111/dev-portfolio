# Inbox Sentinel — Design

**Status:** Design only (no code yet) · **Port reservation:** 8773 · **Date:** 2026-07-07

A local, always-on agent that watches the Outlook inbox **and Sent Items** and turns mail flow into a personal productivity layer: what needs a reply, who owes *you* a reply, what you committed to, and a once-a-day brief — with Claude doing triage and extraction, everything stored locally.

*(Name is a placeholder — rename freely before scaffolding.)*

---

## 1. Problem

Email is where commitments are made and dropped. Three failure modes today:

1. **Needs-my-reply gets buried** — important asks scroll below newsletters and CC-noise.
2. **Waiting-on silently stalls** — you send a question to a GC/vendor/CO and nothing bounces back to you when they don't answer.
3. **Commitments evaporate** — "I'll get you the submittal Friday" lives only in Sent Items.

Existing portfolio apps each watch email for a *domain* purpose; none watch it for *the user's own* productivity:

| Project | What it does with email | Why it doesn't cover this |
|---|---|---|
| email-processor | Classifies inbound RFI/RFQ/RFP opportunities into a vault | Only opportunity mail; no reply/follow-up state, no personal actions |
| project-monitor | Emails → status signals on project entity registers | Project-entity lens, not person lens; ignores anything unmatched to a job |
| cyber-brain | Curated .eml drops → knowledge event stream | Retrospective knowledge, not forward-looking obligations |
| outlook-followup (stub) | Office.js add-in for manual "track follow-up" clicks | Client-side only, no background scanning, never built past design |
| daily-summary | Power Automate digest | No LLM, no state, no follow-up tracking |

Inbox Sentinel is the missing **person-centric** layer. It also subsumes the intent of the outlook-followup stub (server-side, no add-in sideloading) and the daily-summary stub (LLM-generated brief), both of which can be retired if this ships.

Commercial equivalents (Superhuman, SaneBox/SaneReminders, Fyxer, alfred_) validate the feature set — priority triage, no-reply bounce-backs, task extraction, daily brief — but all require handing mailbox content to a SaaS, which is a non-starter under SSi's CMMC posture. Same features, local-first, is the design goal.

---

## 2. Feature set

### MVP (v0.1)

1. **Triage classification** — every new inbox message gets a bucket:
   - `needs-reply` (a person is asking *you* for something)
   - `waiting-on` (auto-created from *your sent* messages that ask a question / make a request)
   - `fyi` (relevant, no action)
   - `noise` (newsletters, automated notices, CC-only chatter)
2. **Follow-up tracking (the SaneReminders feature)** — for each `waiting-on` thread, watch the conversation; if no reply arrives by the due window (default 3 business days, per-thread override), surface it as **overdue**. Reply detection = new message in the same `conversationId` from the counterparty (project-monitor's delta sync gives us this for free).
3. **Commitment & action-item extraction** — Claude tool-use pulls structured items from actionable mail: `{kind: ask|commitment, title, owner: me|them, due_date?, thread}`. Your own sent mail is scanned for commitments *you* made.
4. **Daily brief** — one Markdown/HTML digest at a configured time: overdue waiting-ons, today's needs-replies ranked, open commitments due soon, yesterday's stats. Rendered on the dashboard and optionally dropped as a `.md` into the Obsidian vault.
5. **Dashboard** — FastAPI + session auth (account-store), port 8773: triage queue, waiting-on board with aging, commitments list, per-thread timeline, SSE live updates.
6. **Feedback loop** — every user override (rebucket, dismiss, snooze, mark-done) is logged and the most recent N overrides are injected into the triage prompt (email-processor's decision-feedback pattern, proven in production).

### Explicitly later (not v0.1)

- Draft replies in the user's voice (Fyxer-style) — biggest scope/risk jump, needs `Mail.ReadWrite`+send.
- Writing back to Outlook (flags, categories, To Do tasks) — requires write scopes; MVP is read-only.
- macOS native notifications for overdue items (nice, small, but not core).
- Calendar context (`Calendars.Read`) for deadline-aware ranking.
- Multi-mailbox / shared-mailbox support.

### Non-goals

- Not an email client — Outlook stays the reading/writing surface.
- No auto-sending, ever, without explicit per-message user action.
- No re-implementation of email-processor's opportunity pipeline; if a message looks like an RFP, the brief just links to email-processor's vault entry.

---

## 3. Architecture

```
                 ┌─────────────────────────── Mac (launchd) ───────────────────────────┐
Outlook 365      │  sync daemon                 pipeline                    surfaces   │
┌──────────┐     │  ┌────────────────┐   ┌──────────────────────┐   ┌───────────────┐ │
│ Inbox     │────▶│  │ Graph delta    │──▶│ rules pre-filter     │──▶│ FastAPI :8773 │ │
│ Sent Items│────▶│  │ poll (90s)     │   │ → Claude triage      │   │ dashboard+SSE │ │
└──────────┘     │  │ MSAL device-   │   │ → Claude extraction  │   ├───────────────┤ │
   (fallback:    │  │ code, Mail.Read│   │ → follow-up engine   │   │ daily brief   │ │
   .eml drop     │  └────────────────┘   └──────────┬───────────┘   │ (md → vault)  │ │
   folder)       │                                  ▼               └───────────────┘ │
                 │                        SQLite + FTS5 (state.db)                     │
                 └─────────────────────────────────────────────────────────────────────┘
```

### 3.1 Sync engine (transport decision)

**Decision: delta-query polling, not Graph webhooks.**

- Graph change notifications require a **publicly reachable HTTPS endpoint** and mail subscriptions expire after ~3 days (max ~4,230 min), needing constant renewal. This Mac's Traefik is LAN-only; exposing it to the internet for webhook delivery is a security regression for zero real benefit — 90-second polling latency is indistinguishable from instant for a productivity digest.
- Microsoft's own guidance is webhook-*triggered* delta sync with periodic fallback polling; dropping the webhook leg and keeping the delta poll is the standard single-user-local simplification.
- Mechanism: `GET /me/mailFolders/{inbox,sentitems}/messages/delta` with `$select` projection and `Prefer: outlook.body-content-type="text"`, persisting `@odata.deltaLink` per folder — **this is exactly project-monitor's `sources/graph.py`, reused verbatim**, including its 429/Retry-After backoff. Two folders instead of one is the only change.
- Auth: MSAL `PublicClientApplication` device-code flow, delegated `Mail.Read`, token cache at `<state_dir>/msal_token_cache.json` (0600) — copy of `project-monitor/src/project_monitor/sources/msal_auth.py`.

**Fallback transport (CMMC hedge):** the same `.eml`/`.msg` drop-folder watcher email-processor uses. The pipeline consumes a normalized `IncomingMessage` dataclass either way, so the transport is a config switch (`[source] mode = "graph" | "drop"`). If IT declines delegated `Mail.Read` (cyber-brain is still waiting on that approval; project-monitor got it), the app still works degraded — minus automatic reply-detection freshness.

### 3.2 Processing pipeline (per new message)

1. **Rules pre-filter (no LLM, free):** sender-domain allow/deny lists, `List-Unsubscribe` header ⇒ `noise`, automated-sender patterns (noreply@, notifications@), self-sent CC copies. Expect this to swallow 40–60% of volume before any API call.
2. **Triage call (Haiku):** cheap classification into the four buckets + urgency 1–5 + one-line reason. Prompt-cached system prompt (~1–2k tokens) + recent user-override feedback block. Runs on every message that survives the pre-filter.
3. **Extraction call (Sonnet, conditional):** only for `needs-reply` and own-sent messages — tool-use schema `record_productivity_items` returning asks/commitments/due-dates (project-monitor's `extract/emails.py` pattern). Skipped for `fyi`/`noise`, which is most of the inbox.
4. **Follow-up engine (no LLM):** pure state machine on `conversationId`: sent message with an extracted ask ⇒ open `waiting_on` row; any inbound message on that conversation from the counterparty ⇒ mark answered; nightly job flips past-due rows to `overdue`.
5. **Cost log:** append-only `costs.jsonl` per call (tokens + USD), same as email-processor.

**Cost estimate:** at ~80 messages/day, ~45 surviving pre-filter → 45 Haiku triage + ~12 Sonnet extraction calls/day with cached prompts ≈ **well under $1/day**; the daily brief is one additional Sonnet call over structured rows (not raw bodies), a few cents.

### 3.3 Data model (SQLite + FTS5)

```sql
messages      (id PK, graph_id, conversation_id, folder, from_addr, to_addrs, subject,
               received_at, body_text, bucket, urgency, triage_reason, processed_at)
threads       (conversation_id PK, subject, counterparty, last_inbound_at, last_outbound_at)
waiting_on    (id PK, conversation_id FK, ask_summary, opened_at, due_at,
               status: open|answered|overdue|dismissed, answered_by_msg FK NULL)
items         (id PK, message_id FK, kind: ask|commitment, title, owner: me|them,
               due_date NULL, status: open|done|dismissed, dedup_hash UNIQUE)
overrides     (id PK, ts, message_id FK, field, old_value, new_value)   -- feedback loop
graph_sync    (folder PK, delta_link, last_sync_at)                     -- from project-monitor
messages_fts  (FTS5 over subject, body_text, from_addr)
```

Dedup: `items.dedup_hash = sha256(conversation_id + normalized title)` so re-processing a thread never duplicates an action item. Body text retained locally only; a config retention window (default 90 days) prunes bodies but keeps metadata/items.

### 3.4 Surfaces

- **Dashboard (FastAPI, port 8773):** session auth via account-store + email-processor's CSRF/session middleware. Views: *Triage* (today's needs-reply, ranked), *Waiting On* (aging board, snooze/dismiss/done), *Commitments*, *Brief archive*, thread detail with timeline. SSE for live updates.
- **Daily brief:** generated at a configured local time by the daemon; written to the dashboard and optionally to `<obsidian-vault>/briefs/YYYY-MM-DD.md` for the existing OneDrive/Obsidian habit.
- **CLI (Typer):** `inbox-sentinel auth` (device-code bootstrap), `sync`, `brief --now`, `run` (daemon+web), `status`.

### 3.5 Deployment

- Two launchd agents, following the scribe/email-processor convention: `com.ssi.inbox-sentinel.sync` (daemon: poll + pipeline + scheduled brief) and `com.ssi.inbox-sentinel.web` (uvicorn :8773). Homebrew python per the launchd-TCC rule if the drop-folder mode reads ~/Documents.
- `uv` project, venv at `.venv.nosync` with `.venv` symlink (iCloud rule), `.gitignore` uses `.venv*`.
- State under `~/.local/share/inbox-sentinel/` (db, token cache, auth), logs under `~/Library/Logs/inbox-sentinel/`.

---

## 4. Reuse map (build vs. copy)

| Component | Source | Effort |
|---|---|---|
| MSAL device-code auth + token cache | `project-monitor/src/project_monitor/sources/msal_auth.py` | copy |
| Graph delta sync + backoff | `project-monitor/src/project_monitor/sources/graph.py` | copy, add sentitems folder |
| .eml/.msg parsing (fallback mode) | `email-processor/src/email_intake/email_parser.py` | copy |
| Session auth / CSRF / account-store | `email-processor/src/email_intake/auth.py` | copy |
| launchd templates + entrypoint | `email-processor/scripts/*.plist.template`, `watcher-entrypoint.sh` | adapt |
| Claude tool-use extraction | `project-monitor/src/project_monitor/extract/emails.py` | adapt schema |
| Decision-feedback prompt injection | email-processor pattern | adapt |
| Cost logging (costs.jsonl) | email-processor pattern | copy |
| SQLite + FTS5 layer | `cyber-brain/src/cyber_brain/db.py` | adapt schema |
| **New:** follow-up state machine | — | build (~small, pure logic) |
| **New:** rules pre-filter | — | build (small) |
| **New:** triage prompt + brief generator | — | build (prompt work) |
| **New:** dashboard views | — | build (largest new surface) |

Roughly: transport/auth/storage ~80% off the shelf; the genuinely new code is the follow-up engine, the prompts, and the UI.

---

## 5. Security & privacy

- **Read-only Graph scope (`Mail.Read`) in MVP** — the app cannot send, modify, flag, or delete mail. Every "later" feature that needs write access is a separate, explicit consent step.
- Mail bodies never leave the Mac except to the Claude API (already the accepted posture for email-processor/project-monitor). No third-party SaaS sees the mailbox — the point of building instead of buying SaneBox/Fyxer.
- Token cache 0600; dashboard binds `127.0.0.1` by default (LAN exposure via the existing Traefik pattern only if wanted later); account-store session auth on all routes.
- Retention pruning of bodies (default 90 days) limits blast radius of the local DB.

## 6. Risks & open questions

1. **IT approval for delegated `Mail.Read`** — project-monitor sets precedent, cyber-brain's request is still pending. Mitigated by the drop-folder fallback, but the product is materially better with Graph. *Resolve before scaffolding.*
2. **Triage quality on day one** — buckets will misfire until the feedback loop accumulates overrides. Mitigation: launch in "observe" mode for a week (classify + log, no notifications) and tune the prompt against real traffic before trusting the brief.
3. **Sent-items ask detection** — deciding "this sent email expects a reply" is the fuzziest LLM judgment in the design; false positives create waiting-on clutter. Mitigation: require explicit question/request markers at first, loosen with feedback.
4. **Overlap creep with project-monitor** — both extract action items from the same inbox. Boundary: project-monitor owns *project-entity* state; Sentinel owns *personal* obligations, and links out rather than duplicating. Revisit if the two item lists start converging.
5. **Which mailbox** — design assumes the SSi M365 work mailbox. Personal Gmail would need a second transport (IMAP/Gmail API) — out of scope unless requested.

## 7. Build phases (when greenlit)

1. **P1 — Sync skeleton:** MSAL auth + two-folder delta sync + SQLite persistence + CLI `sync`/`status`. *Verify: messages land in DB incrementally, delta resumes across restarts.*
2. **P2 — Pipeline:** pre-filter + Haiku triage + Sonnet extraction + cost log, observe-mode. *Verify: a week of real mail, spot-check bucket accuracy ≥ ~85% on needs-reply.*
3. **P3 — Follow-up engine + brief:** waiting-on state machine, overdue detection, daily brief to vault. *Verify: seeded threads flip open→answered→overdue correctly across the due window.*
4. **P4 — Dashboard + daemons:** FastAPI views, SSE, override capture feeding the prompt, launchd agents. *Verify: end-to-end soak, overrides visibly change subsequent triage.*

Each phase is independently shippable; a sliced `.plans/` breakdown gets written when implementation is approved.
