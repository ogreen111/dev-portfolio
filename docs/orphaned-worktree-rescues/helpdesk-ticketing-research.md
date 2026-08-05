# Help Desk Ticketing Research — Replacing SolarWinds

**Date:** 2026-07-08 (rev. 2 — assumes full Microsoft Graph mailbox access, per the SENTRY pattern)
**Question:** IT is unhappy with our SolarWinds help desk (main complaint: searching and scrolling through email threads for each ticket). What else is on the market, and could we build our own internally?

**Method:** Multi-agent deep-research sweep (102 agents; 93 claims extracted, each adversarially verified 3-vote against primary sources — 17 confirmed, 8 refuted) plus two targeted follow-up verification passes (JSM/Zendesk; the open-source field). Pricing fetched/verified 2026-07-08; all SaaS prices are annual-billing floors unless noted (monthly runs 10–50% higher).

**Standing assumption:** we have full control of Graph app registrations in our M365 tenant and already run Graph-based inbox monitoring (SENTRY), so any integration path — Graph mailbox connection for a self-hosted tool, OAuth mailbox connection for SaaS, or a Graph-native internal build — is technically open to us.

---

## TL;DR

1. **The email-scrolling complaint is table stakes, not a differentiator.** Every modern product converts email threads into ticket-threaded conversations using Message-ID/subject-token matching. Any credible option fixes the stated pain, so the decision reduces to hosting model, integration depth, price, and how much we want to own.
2. **Nearly everything is cheaper than SolarWinds.** The incumbent baseline (SolarWinds Service Desk Essentials) is **$39/agent/month** (verified against SolarWinds' pricing page). Freshservice starts at $19, ManageEngine at ~$13, Zendesk Support at $19, JSM Standard at ~$20, Zammad SaaS at €7–25 — and self-hosted Zammad/FreeScout are license-free.
3. **Best buy/adopt candidate: self-hosted Zammad.** Native Microsoft 365 **Graph API** email channel (unique among everything surveyed), explicitly tunable multi-signal threading, Elasticsearch search over tickets *and* attachment contents — the direct antidote to the search complaint — at €0 license.
4. **An internal build is genuinely viable — more than generic build-vs-buy wisdom suggests — because Graph does the hard part.** Exchange computes conversation threading server-side (`conversationId`), so a Graph-native internal tool inherits the threading that Zendesk/Atlassian/Freshservice implement as fragile Message-ID/subject-token heuristics (all three maintain KB articles for their misthreading failure modes). With our existing Graph patterns, a production MVP is a realistic **~6–10 week single-engineer project** — but it competes against a €0-license product that already does everything, so the honest justification for building is customization/AI integration/ownership, not cost.
5. **Recommended path:** pilot self-hosted Zammad for a week of real tickets (1–2 days to stand up). In parallel, if the build appetite is real, a 2–3 day Graph+SQLite spike will tell you more than any estimate. Either way, put internal engineering into a Claude triage layer on top — that's the differentiating piece nobody sells.

---

## 1. The incumbent baseline

- **SolarWinds Service Desk Essentials: $39/agent/month** — verified against SolarWinds' own pricing page and G2/Capterra (June 2026). A blog claim describing a "$39 Team → $99 Enterprise" ladder was refuted 0–3; only the $39 Essentials figure survived verification.
- At, say, 10 agents that's **~$4,680/yr** — a useful yardstick: every serious alternative below undercuts it 2–3×, and the self-hosted options undercut it entirely.

## 2. Commercial products (verified facts)

| Product | Price (annual billing, per agent/mo) | Hosting | Email-to-ticket threading | Notes |
|---|---|---|---|---|
| **Freshservice** | **$19** Starter / $49 Growth / $99 Pro / Enterprise quote (vendor page) | **SaaS only** (no on-prem; only discovery/orchestration agents run locally) | Dual-signal: Message-ID header **or** `[#ticket-id]` subject token, plus a requester check; replies without a valid marker can duplicate tickets (vendor KB) | Cheapest mainstream full-ITSM entry; a $95-Pro blog claim was refuted — it's $99 |
| **ManageEngine ServiceDesk Plus** | **~$13** Standard / $27 Pro / $67 Ent (vendor page, "starts from"; 2–1 split vote on cloud-vs-on-prem attribution of the $13) | **Cloud AND on-premises** — one of the few commercial on-prem options | Standard header/subject matching | Cheapest broad-feature commercial tier; Standard lacks asset mgmt |
| **Jira Service Management** | ~$20 Standard / ~$48 Premium (third-party trackers; Atlassian's JS-rendered pricing page couldn't be fetched — treat as approximate). Free tier: 3 agents | **Cloud only for new buyers** — Data Center new sales ended **2026-03-30**, read-only EOL **2029-03-28** (Atlassian EOL page) | Header-driven (Message-ID / In-Reply-To / References); M365 mailbox via OAuth. At least 5 separate Atlassian KBs document misthreading modes (replies spawning new tickets, reused threads landing as comments) | Practitioner sentiment (anecdotal, competitor-quoted): admin-heavy, clunky as a pure helpdesk |
| **Zendesk** | **$19** Support Team (ticketing only) / **$55** Suite Team / $115 Suite Pro (vendor page) | **SaaS only** | Most redundant matching of anything surveyed: headers + encoded Reply-To ID + hidden body token + bracketed ID in outbound mail (vendor docs). Still has documented duplicate/wrong-ticket modes when forwarders strip headers | Support Team tier is a decent pure-helpdesk fit; Suite pricing escalates fast |
| **HaloITSM** | ~$49+/agent (verifier context, not a surviving primary claim) | **SaaS AND self-hosted** (published on-prem spec: SQL Server + Windows Server, 8 GB RAM) | Standard | The mid-market "both hosting models" option, but Windows/SQL Server stack doesn't match our tooling |
| **Spiceworks Cloud Help Desk** | **$0** (ad-supported, unlimited techs/tickets); ~$6 Premium (June 2025) removes ads | **Cloud only** (on-prem retired) | Basic | The budget floor; ad-supported freemium; vendor site blocked crawlers so vendor-page confirmation is indirect |
| **Zammad SaaS** | **€7** Starter (max 5 agents) / €16 Pro (max 35) / €25 Plus (vendor pricing page; monthly = €9/18/27) | SaaS (self-hosted covered below) | See §3 | The SaaS fallback if self-hosting Zammad ever gets old |

**Refuted along the way (do not reuse these numbers):** JSM at $18, Freshservice Pro at $95, ManageEngine cloud at $10/$21/$50, SolarWinds "$39 Team→$99 Enterprise" ladder, and Zammad's claimed WhatsApp/SMS/X channel list.

## 3. Open-source / self-hostable options (verified 2026-07-08)

| Product | Activity (2026) | Stack | M365 email path | Search | Verdict for us |
|---|---|---|---|---|---|
| **Zammad** | Active; v6.5+ | Ruby/Rails; **PostgreSQL 13+, Redis 6+ required; Elasticsearch optional-but-strongly-recommended**; min 2 cores / 6 GB RAM (+4 GB if ES co-hosted → ~10 GB single box) (official docs) | **Only surveyed product with a native Microsoft 365 Graph API channel** (≥6.5, "the future-proof way" per docs) + M365 IMAP/XOAUTH + Fetchmail/Sendmail | **Elasticsearch-backed** — fast at volume, indexes attachment contents | **Primary candidate.** Tunable multi-signal threading (subject hook, References/Message-ID, body/attachment scans) with documented precision/recall tradeoffs |
| **FreeScout** | Very active — v1.8.229 (2026-07-04), near-weekly releases, ~4.4k stars | PHP/Laravel + MySQL/Postgres; runs on tiny hardware | Delegated OAuth over IMAP (official wiki) **+ community Graph API module** (send & fetch) | MySQL-based; degrades at scale; official paid Meilisearch "Faster Search" module is the remedy | **Lightweight fallback.** AGPL core + one-time-fee paid modules (that's the business model — budget for a few) |
| **osTicket** | Active — v1.18.4 (2026-06-17), ~3.8k stars | PHP + MySQL; lightest footprint | IMAP/POP polling with OAuth2-Microsoft (XOAUTH2 over IMAP — no Graph); MTA-pipe fallback | MySQL FULLTEXT; **devs themselves acknowledge relevance problems** and a 500-result cap (GH #4972) | Weak on our exact pain point (search); pass |
| **Request Tracker (RT)** | Active — rt-6.0.3 (2026-05-20), enterprise-grade, Best Practical | **Perl** + PG/MySQL; MTA-piped (`rt-mailgate`); heaviest ops burden for a non-Perl shop | **App::wsgetmail fetches via Graph** (client-credentials service principal) — works for us, but the module has bus-factor 1 | Best of the OSS group: native DB full-text indexing (PG tsvector/GIN) | Capable, but Perl and the ops model don't fit our stack; pass |
| **GLPI** | Very active — v11.0.8 (2026-06-24), ~6.1k stars | PHP + MariaDB; full ITSM+asset suite (big surface) | IMAP/POP collector; M365 OAuth via `oauthimap` plugin (delegated, over IMAP); no Graph path found | Criteria/filter search, **not true full-text**; documented complaints: followups not searched (GH #2092), 30 s pages at ~40k tickets (GH #15246) | Search weakness; pass |
| **UVdesk** | **Stalled** — last release 2025-09, no pushes since 2025-10; stars look marketing-driven (19.3k stars / 566 forks) | PHP/Symfony (4-era) | IMAP with app passwords (legacy auth); OAuth documented only in a vendor blog; no Graph | Basic; unverified | Pass |
| **Peppermint** | Pre-1.0, single maintainer, sporadic commits | TS/Next.js + Postgres | **M365 effectively broken** (open issue requesting OAuth2 for EXO); no Graph | None documented | Pass |

**Note on refuted Zammad TCO figures:** blog claims of €345–810/month operating cost, "4 GB RAM minimum," and €2,999/yr support were refuted or unverified. Use the official requirement (2 cores / 6–10 GB RAM, PG + Redis + optional ES) and estimate ops cost ourselves — this is a stack we already run heavier versions of.

## 4. Build: what an internal version would actually look like

Since we control Graph and already run Graph inbox monitoring (SENTRY), an internal build is a real option, and it's stronger than generic build-vs-buy wisdom suggests — because **Graph eliminates the hardest problem**.

### Why Graph changes the difficulty

The verified market evidence shows email reply-threading is where mature vendors bleed: Freshservice requires a `[#ticket-id]` subject token and can duplicate tickets without it; Atlassian maintains at least five KB articles on JSM misthreading; Zendesk stacks four redundant matching signals and still documents wrong-ticket threading when forwarders strip headers. All of them are re-deriving conversation structure from raw RFC-822 headers because they sit outside the mailbox.

A Graph-native tool sits *inside* the mailbox: **Exchange computes `conversationId` server-side** for every message, replies included, and Graph exposes it directly. Replies sent via Graph's `reply`/`createReply` actions stay in the same conversation for the requester in Outlook. The threading problem that costs vendors KB articles mostly disappears; what remains is the tail (subject-change splits, users starting fresh emails about an old issue — handled with a subject-token fallback and a manual "merge into ticket" action).

### MVP scope sketch

| Component | Approach | Notes |
|---|---|---|
| Ingestion | Graph subscription webhooks on the helpdesk shared mailbox, with delta-query polling as the reliability backstop | Same pattern as SENTRY; subscriptions need periodic renewal — the classic operational gotcha |
| Threading | `conversationId` grouping + `[#ticket-id]` subject-token fallback + manual merge | Inherit Exchange's threading instead of reimplementing it |
| Ticket model | SQLite: tickets, messages, agents, status/priority, event log | Familiar stack; trivial to back up |
| Search | **SQLite FTS5** over subject/body (+ extracted attachment text if wanted) | Directly answers the SolarWinds complaint; proven at this scale |
| Assignment/status/SLA | CRUD + due-time timers + escalation notifications | The genuinely easy part |
| Outbound | Graph `reply` from the shared mailbox | Requester experience stays plain email |
| UI | FastAPI + server-rendered UI, `account_store` auth | Existing house patterns |
| AI layer | Claude triage: categorize, prioritize, summarize thread, draft first response | The piece no vendor sells the way we'd build it |

### Effort and pitfalls (judgment — flagged)

No sourced build-effort data survived adversarial verification, so these are engineering estimates, not citations: a production-quality MVP of the above is a realistic **6–10 week project for one engineer**, with the risk concentrated in operational details rather than architecture: webhook subscription lifecycle, delta-token bookkeeping, HTML email sanitization, attachment storage, **auto-reply loop prevention** (out-of-office storms are the classic self-inflicted outage), spam handling, and migrating/retiring SolarWinds history. Post-MVP, expect steady feature pull (reporting, KB, asset links, customer portal) — that's where internal tools quietly grow into part-time products.

### The honest comparison

The build doesn't compete with SolarWinds' $39/agent — it competes with **Zammad at €0 license**, which already ships threading, search, SLA, reporting, a KB, and a decade of edge-case fixes. So the case for building is *not* cost. It's legitimate when you weight:

- **Fit/ownership** — a tool shaped exactly to IT's workflow, in a stack we fully own, joining an existing portfolio of self-hosted internal apps;
- **AI-first design** — Claude triage/summarization/drafting as a first-class feature rather than a bolt-on;
- **Simplicity** — one FastAPI/SQLite service vs. a Rails + PostgreSQL + Redis + Elasticsearch appliance (~10 GB box) to operate and upgrade.

And it's the wrong call if IT needs vendor-grade reporting/ITIL features soon, if the 6–10 weeks can't be protected, or if nobody wants to own the pager for the company's ticket system.

**Hedge worth naming:** whichever way this goes, the Claude triage layer is worth building — Zammad has a full REST API and webhooks, so the same AI layer (~2–4 weeks) works in front of a bought system or a built one. It's the differentiating piece and it's portable across the decision.

## 5. Recommendation framework

**Path A — Adopt (default): self-hosted Zammad.**
Stand it up via official docker-compose (~10 GB RAM box: app + PostgreSQL + Redis + Elasticsearch), connect the helpdesk mailbox through its **native Graph channel**, and run a 1-week pilot with two or three techs on real tickets. Elasticsearch search across tickets and attachment contents is the direct fix for the "search and scroll through emails" complaint — let the unhappy team feel it before deciding. Cost: €0 license + our ops time; SaaS fallback at €16/agent if self-hosting palls.

**Path B — Buy SaaS (if IT wants zero ops):** Freshservice Starter ($19) or ManageEngine ServiceDesk Plus Standard (~$13) — both under half the SolarWinds bill; ManageEngine also has an on-prem edition if that's ever preferred.

**Path C — Build (if the fit/AI/ownership case resonates):** run a **2–3 day spike first** — Graph subscription on a test mailbox → SQLite + FTS5 → minimal ticket list with conversation grouping. The spike retires the two real risks (webhook lifecycle, conversationId behavior on your actual mail) and makes the 6–10 week estimate concrete before committing.

**Decision rule:** pilot A while spiking C if build appetite exists; pick B only if self-hosting is off the table. In every path, build the Claude triage layer — it's portable across all three.

---

## Appendix: research quality notes

- Adversarial verification killed 8 of 25 tested claims — notably *all* pricing from one listicle (flamingo.run) and Zammad TCO/hardware figures from openmsp.ai. Every price in this report traces to a vendor page fetched 2026-07-08 or is explicitly flagged as third-party/approximate (JSM).
- **Remaining gaps:** ServiceNow was not evaluated (nothing survived verification; it's enterprise-priced and out of scope for a small team anyway). HaloITSM's ~$49 figure is verifier context, not a confirmed primary claim — confirm before shortlisting it. Practitioner complaints in §2 are anecdotal, several via competitor marketing pages, and flagged as such. Build-effort figures in §4 are engineering judgment, not sourced claims — no build-vs-buy effort data survived verification.
- Primary sources relied on: Zammad admin docs (Graph channel, threading settings, hardware/software prerequisites), Freshservice support KBs (threading rules), Atlassian support KBs + Data Center EOL page, Zendesk pricing page + threading docs, ManageEngine pricing page, Freshworks pricing page, GitHub repos/releases for all OSS products, Best Practical RT 6.0.3 docs + App::wsgetmail, FreeScout official wiki, GLPI plugin docs.
