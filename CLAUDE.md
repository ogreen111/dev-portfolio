# Dev Portfolio — Claude Context

This is the `dev-portfolio` git repo, checked out in two places on this
Mac: `~/dev/` (primary, non-iCloud-synced — the destination for the
project relocations below) and `~/Documents/dev/` (the original
iCloud-synced workspace every project in the registry below that needed
relocating has now been moved out of — see the "lives outside this tree"
notes below for the full history; a few registry entries, like `scripts`,
`deploy`, and vendored third-party code, were never part of
`~/Documents/dev`'s own tracked history and needed no relocation). The
registry below mirrors the full 31-project portfolio, organized around
three core domains:

1. **DoD/MILCON cybersecurity proposal automation** — RFP intake → pricing → tech proposal → EAC tracking
2. **BAS/OT network engineering** — passive discovery, BACnet simulation, site scanning, hardware prototypes
3. **SSi internal productivity** — email triage, project financial tracking, past-performance management

---

## Project Registry

| Project | Purpose | Status |
|---|---|---|
| rfp-automation | DoD RFP intake, scope extraction, proposal drafting; missing-RFP-docs flag surfaces MISC folders with an empty `0.RFP/` that `discover_projects` would otherwise drop silently (`RFP_MISSING_DOCS_ENABLED`), now requiring numbered-scaffold evidence (`^\d+\.`) so scratch dirs and pre-intake dumps don't false-fire, and as of 2026-08-13 keyed on `<library scope>/<folder name>` rather than the resolved absolute path (a mount-alias drift was rewriting every key and losing every acknowledgment; legacy keys auto-migrate, and a scope counts as scanned only once every same-named claimant read successfully in that round); GovWin IntelliSearch ingest now rides the existing rfp-intake mailbox poll (the 2026-08-08 folder-polling wiring was removed the next day) and is a no-op unless `RFP_GOVWIN_MAILBOX_INGEST_ENABLED` is set, with the `govwin_ingest` CLI still available standalone over a folder of `.eml` files; watcher hardened 2026-08-10 against a stalled OneDrive root raising `TimeoutError` out of ordinary `Path` calls; **nine-slice Graph Files API migration** (`.plans/graph-migration/`) replaces the OneDrive-sync dependency with direct Graph reads/writes over a `/delta`-refreshed local cache mirror — slices 01–04 done, 05–08 partial (primitives + a widening set of call sites: deliverable + ingestion write-through, dashboard serving, Graph-aware `process_project()` reads, and as of 2026-08-12 `cyber_summary.py` + `cyber_spec_extractor.py`; crash-safe outbox, `If-Match` on simple-PUT overwrites (the chunked >10 MiB path is advisory-safe only), hardcoded fail-closed site+drive allow-list, `docs/CMMC_GRAPH_FILES_ADDENDUM.md`), 09 blocked on the pilot soak; 2026-08-12/13 was a concentrated correctness pass over that migration — a local `_email_attachments/` overlay (incl. ZIP members) so pipeline-synthesized attachments aren't invisible to Graph-backed parsing, `graph_cache` delete-and-reupload recovery with full ancestor healing, and a `resolve()` stale-snapshot race closed; 08-13 continued it with ZIP-member resolution through `archive_utils`' content-addressed cache, `pending_upload` preserved across a delete-and-reupload identity change, and a broad `RuntimeError` catch replaced by a network-free `list_entries()` known-folder check so genuine Graph failures propagate; **no longer inert as of 2026-08-14 — the live `.env` now sets `RFP_GRAPH_BACKEND_ROOTS=misc,umcs_v,mrr_vii`, so all three roots are opted in and the watcher takes an Azure AD token every poll**; 08-14 also resolved PLAN.md open question #1 (the 4th SharePoint site, SSI Fileshare, hosting `RFP_STAGING_ROOT` + proposal templates — live-verified read/write, added to `ALLOWED_ROOTS`, covered by the existing `Sites.Selected` grant with no new IT ticket; remote delete 403s under a likely retention hold, harmless since write-through never deletes; wiring its call sites is still slice-06 work) and made `GraphCache` build one `GraphAuth` per instance instead of letting 14 call sites each request a fresh token (latency only, dozens of redundant AAD round-trips per parse). Also 08-13: `riser_diagram_extractor`'s sheet-index build takes a page-count-scaled timeout (8s/call budget — a measured average with margin, not a proven per-call bound — floored at the 240s default, capped at 800s, page count peeked in a subprocess), and SENTRY's pre-push CI gate runs ruff/mypy against an isolated `git worktree` pinned to the captured sha instead of stashing the shared working tree (a stash-pop conflict had orphaned real work on 08-12) — it still fast-forwards the primary checkout's local main onto a gate-generated ruff-fix commit, and if `git worktree add` fails it logs "gate skipped, push proceeds unchecked" rather than failing closed; a non-fast-forward push rejection is now classified `blocked_diverged` for a human, never auto-healed. A 2026-08-12 `ImportError` regression (`apply_force_drawing_matches`, a call to a function that was never implemented) had been silently failing every non-locked project's run until it was found and removed. **Infra incident, worked around not fixed (not a code defect):** the macOS File Provider remounted the SharePoint library into four `*SpectrumSolutionsInc*` mount points and the canonical one every `RFP_PROJECT_ROOTS` path targeted lost the UMCS and MRR libraries, so `discover_configured_projects` (which skips a missing root silently) saw one project per poll, `monitor_dashboard.json` collapsed from 230 projects to 1, and a real amendment on an active bid stuck in `needs_review` with the manual-merge path blocked too; on 2026-08-11 ~09:42 the operator repointed `RFP_PROJECT_ROOTS` at the fully-synced `...SpectrumSolutionsInc 2` duplicate mount and discovery returned to 232 projects with no data lost — but the canonical mount is still collapsed on disk and the File-Provider cause is still unexplained, so a `.env` revert or a stalled duplicate mount reintroduces it. That incident got worse on 2026-08-14 (OneDrive found fully uninstalled — no process, no app bundle, CloudStorage mounts empty shells — explaining a wave of Errno 60 timeouts) and bottomed out on 08-15 with no library mounts at all. **Slice 10 (2026-08-15, `10-deliverable-output-relocation.md`) closed the "discovery is still purely local" gap**: `discover_configured_projects()` routes Graph-backend-enabled roots through `discover_projects_graph()`, and all output under `resolve_project_output_dir()` writes to the GraphCache mirror (`~/Library/RFPAutomation/graph_cache/<site_key>/...`) rather than the OneDrive tree, raising `GraphOutputUnavailable` rather than ever falling back to a broken mount. Its documented gaps: the end-of-run push sweep never propagates local deletes, and hydration is best-effort per file. The pre-push review gate caught 8 real bugs across two rounds on that slice (unresolved mirror dirs, double-resolution silently dropping pushes, hydration scoped too narrowly, stale bytes left after a failed hydrate, `apply_fixes()` marking a `GenuineConflict` as applied, and only 3 writers pushing at all); the pricing workbook needed three attempts before deriving `graph_relative_path` inside `pricing_builder` instead of predicting a filename. **2026-08-16 was a live production outage and the dashboard read-path migration that answered it:** the dashboard's project-record walk — the largest item still on slice 10's not-yet-covered list — was walking the local tree when the macOS File Provider's `readdir` hung, pegging watcher and dashboard at 100% CPU and blanking every page. Overnight into 08-17, `_find_project_records_uncached()` in `dashboard_site.py` (behind `/api/dashboard`, `/api/intake`, `/api/followups`), the other summary-dir walkers (`_build_slug_index`, `_find_project_detail_by_slug`, primes POC roster) and `opportunity_discovery.load_queue` moved onto GraphCache with zero live-mount I/O; `_record_search_roots()` now keeps Graph-enabled roots *without* a local `.exists()` probe, so an unmounted root can no longer collapse the dashboard to zero. `project_rename.py`'s husk reaper (a destructive local `rmtree` sweep) skips Graph-enabled roots instead, hardened over five gate rounds to fail **closed** — strict site-key mapping parse, raw-env backend check, mapped-root-is-never-local, explicit-but-invalid entries rejected; a Graph-native reap is follow-on work. `resolve_project_output_dir()`'s mirror branch now probes `_tech_summary_candidates` order for the layout that actually holds `run_status.json` (always building `Cyber/` had silently dropped 70 legacy-layout projects plus one dual-layout project). `DashboardRequestHandler` declares `protocol_version = "HTTP/1.1"` — observed, not a proven causal chain: under the HTTP/1.0 default ~20 stuck-ESTABLISHED sockets accumulated and every request after the first hung, and HTTP/1.1 plus the Content-Length audit it forces (5 redirects fixed) and `close_connection = True` on pre-body-read rejections cleared that hang class live. Latency work, each pinned by a regression test: single-flight records cache with stale-while-revalidate on a 120s TTL plus startup pre-warm, `_cached_payload(ttl_seconds=120, background_revalidate=True)` on the heavy payloads, a 4s time-box on `/api/intake` enrichment, and in `graph_cache` read-only index loaders, a reused children map in `_resolve_path_to_id` (was rebuilding from 65k entries per resolve), one `batch_writes()` flush per root (was a 55MB index rewrite per project), and `cancel_pending_upload()`. Frontend `fetchJson()` aborts via `AbortController`. Warm `/api/dashboard` ~40ms, all pages sub-2s warm. **Both prior degradations are resolved as of 2026-08-17:** the `.env` revert landed, all three `RFP_PROJECT_ROOTS` resolve against the canonical mount, and `/healthz` is `ok` on every gate (project_roots 3/0 unavailable, runtime "current," state_integrity 3/0 invalid), ending the 7,501-check 503 streak; watcher baselined at **257 projects**, dashboard serving 248 records. Still true: `monitor_payload` validates shape and never count, so it would not catch a registry collapse. Still not covered by the output-path work: `amendment_review.py`, `cmd_validate`'s live-draft glob, `governing_spec_request.py`'s RFI fallback, and the default-off comment-fixer. SENTRY overnight into 08-17 recurrence-tracked rather than queuing new work: item #64 (`_max_download_bytes()` reusing `config.max_pdf_bytes()`, so any file >500 MB can never `resolve()` — confirmed live on 5.26 GB and 783 MB riser PDFs) is **still unfixed** and gained a hard pipeline-crash variant; item #63's `CorruptDownload` size mismatch stays queued pending an etag-confirmed re-fetch; item #65 is a >2h `monitor_runtime.json` heartbeat freeze with the watcher demonstrably alive — the loop's own pre-commit review corrected its first theory (the three repeated startup banners are legitimate `os.execv` self-reexecs on source-mtime change, which preserve the PID, not `run_monitor()` re-entry), the freeze itself is unexplained, and it has since resumed advancing without a restart. Auto-applied: a 255-byte cap on `graph_cache`'s atomic-write temp filenames. **2026-08-17 answered a second overnight false-alarm outage and closed out two SENTRY items.** The `dashboard-healthcheck` agent had kickstart-looped a *healthy* dashboard all night: `/healthz` 503'd whenever a Graph-enabled root's OneDrive mount was unreachable (irrelevant post-migration) and its monitor probe blocked past the 15s watchdog timeout on every post-restart cold build. The deep check now excludes Graph-enabled roots from the local mount probe (live `/healthz` accordingly reports `project_roots` configured 0 / unavailable 0), serves the monitor check from cached records without ever building inline (fresh records exercise the full payload builder with rows **injected** — `_build_dashboard_payload(records=...)` — to close a freshness TOCTOU), self-recovers through a single guarded background revalidation worker, and escalates to a real 503 only via grace-gated failure tracking (`_RECORDS_REVALIDATION_HEALTH`: consecutive-failure + hung-attempt + one bounded last-chance window, with per-root Graph mirror-index clocks on time-based sync-durability so fast-failing sync attempts never earn the 1-hour hydration ceiling); a new `graph_indexes` check surfaces per-root index outages that a healthy portfolio would otherwise mask. Cache correctness under mutation was fenced the same day: `_CACHE_GENERATION` guards every records/payload store (a build spanning a reviewer POST's invalidation serves its caller but never repopulates the caches — check+write atomic under the payload lock), `do_POST` invalidates before *and* after the mutation (`_dispatch_reviewer_post`), `cold_since` moves only on the populated→cold transition, and cold waiters retry after a fenced store (bounded, with a `_RECORDS_LAST_GOOD` snapshot as the exhausted-retry fallback) instead of surfacing an empty portfolio. `/api/intake` and `/api/followups` — the last two heavy read-only payloads outside `_cached_payload` — moved onto the 120s background-revalidate policy (intake had been paying its 4s enrichment time-box on *every* request against the dead mounts; measured 4.2s→~4ms warm, followups 1–2s→~4ms). That evening a project-paths sidecar was retained from each successful record walk so a project-detail click reads ONE project's JSON directly instead of repeating the whole Graph-backed portfolio walk for one slug (survives ordinary state-cache invalidations, atomically replaced by the next successful record build, falls back to the full walk on cold start or a rename), alongside further read-only `graph_cache` paths that avoid deep-copying the 65k-entry index to build a derived children map. **Item #65 finally got its first concrete, code-level root-cause candidate** (queue-only, deliberately not applied): `_maybe_run_missing_docs_sweep()`'s `os.scandir(root)` (`missing_docs.py:259-265`) runs synchronously and unconditionally — no Graph-backend gate — *before* the heartbeat write `update_monitor_runtime()` (`main.py:8861` vs `:9012`), so a File-Provider `readdir` hang delays the heartbeat by exactly the hang duration, matching this window's two gaps (~94 min and ~71 min); `missing_docs.scan()` is the one walker the dashboard read-path migration never covered, still calling `os.scandir()` on the local root directly. Not proven (the gap had already ended before it was investigated, and this window also showed the first observed self-heal — 162.4 min stale, fresh ~13s later), and the fix is watch-loop control flow, so it stays queued. The 2026-08-16 deep-scan `"projects": 0` anomaly is **closed as resolved** — both aggregators now report 248 projects with plausible buckets, never root-caused, reopen if it recurs. Item #64 gained one more recurrence (RobinsAFB ATC Tower riser diagram, 741 MB, ×128 log lines) and is still unfixed. 2026-08-18 was quiet by comparison — two fixes, three queue entries: `sentry_watch` now bases heartbeat staleness on `monitor_runtime.json`'s `updated_at` content rather than file mtime (`dashboard_site._load_runtime_state` rewrites that file whenever anyone loads the dashboard, refreshing mtime without touching `updated_at`, so the check went blind to a stuck watcher the moment a human opened the dashboard — an observer effect relevant to item #65), and `scripts/archive_old_snapshots.py`'s `_archive_files()` stopped unlinking candidate files whose `tar.add()` had failed (silent data loss); that find produced **item #67** (the archiver is wired to nothing — no launchd agent, cron, or wrapper — so the state dir has grown unbounded to 47k+ files; wiring it stays queued since it would delete live state files on a schedule) and **item #66** (`match_candidates`' top-3 suggestions omit the correct project for a truncated BuildingConnected addendum subject — RHV06/FSB Addendum 01, attachment never auto-fetched; same shared intake-matching surface and do-not-auto-apply reasoning as #52/#26). Recurrence bookkeeping otherwise: two hits deduped against queued items #00 and #18, the benign 404 `GET /drives/items` hydration-probe pattern logged twice more (JBLM McChord, live-data check clean, still not worth a suppressor), all three deep-scan aggregators clean, and #63/#64/#65 still queued and unfixed. 2026-08-19 added one auto-applied fix (`bc74454`): the pipeline logger's sticky context — set by the last `process_project()` stage transition, never cleared — was bleeding a stale slug into `_post_portal_login_comments()`'s own `log()` calls, so a comment posted for one project logged under another's slug; both calls now pass `project_slug=` explicitly. Log attribution only, **no pipeline behavior change**, but it corrupts the per-project evidence trail SENTRY itself reads, and it is a recurrence of the *class* fixed at the PIID-dedup call site on 2026-07-08 (`faeb3c4`) — the durable fix (scoping/clearing the logger context, auditing other call sites) was not done. 2026-08-20 produced no code changes at all — the quietest day in this project's recent history, entirely recurrence bookkeeping. Item #35's `_SUB_DUE_TRIGGER` phrase-coverage gap hit a **fourth** time (Ft. Campbell ATCT, SmartBidNet Addendum 003: "We are requesting quotes by Thursday, September 3rd"), and unlike the first three this one carries real damage rather than a coincidence — the addendum extends the bid date to Sept 3 while the notification's own header field still reads Sept 2, and with no sub-deadline trigger matching, the next full pass will resolve to the stale Sept 2 value, a genuine one-day miss; still queued not auto-applied, since it touches due-date extraction like #25/#32/#34. Item #00's benign ProjNet RFI notification display-link gap logged a fourth recurrence too (RHV06 FSB Efforts, twice that day), and the overnight systemic review came back clean. That call-site audit landed on 2026-08-21 as `6a747c5`, the **third** instance of the same sticky-context fix — `_maybe_run_missing_docs_sweep()`'s portfolio-wide log lines (success *and* failure paths) now pin `project_slug=""`/`stage="missing_docs"` explicitly — and it reached one layer deeper than its two predecessors: `log_exception()`'s own `if project_slug` guard treated an explicit `""` the same as unknown/`None`, so the failure-path line stayed exposed to the bleed even after the caller passed it. The durable fix (scoping or clearing the logger context wholesale) is still not in; three call sites have now been patched one at a time. The rest of 08-21 was queue work rather than code. The RHV06 stale Project-Info-"Solicitation"-row vision-QC false-positive filter has now absorbed **eight** Codex review rounds across three sessions, each finding a real gap, and still carries two open ones — a `Finding.location` bypass (a response shaped `location="Project Info", finding="Solicitation is blank"` never matches a predicate that only reads `finding`/`quoted_text`), and a genuine "Project Info panel failed to render, so solicitation cannot be verified" claim it would swallow as information loss. Its candidate fix (a pricing / grand-total exclusion closing round 7's compound-BLOCKER gap, where instruction 1 escalates multiple empty panels into one BLOCKER that can carry a real empty-pricing defect) sits **uncommitted in the working tree** under an explicit "do not auto-apply, do not resume from this diff as-is" note, plus a direction change: implement the proposed anchor-phrase narrowing instead of excluding one more keyword per round, a shape that is demonstrably not converging. Round 8 also flagged the filter's own docstring claim about a "correspondence section chip" as unsupported by the current renderer — don't cite it as grounding. A second entry queued a possible **cross-solicitation misroute**: a `matched` intake event for a "DB Replace Chiller B0210" bid invite routed to slug `usaf_b1947_replace_lights_shawafb`, whose entire prior history is Replace-Lights-B1947 traffic; blocked on a fresh `match_project` repro against the saved `.eml` before any live-data repair, since a confirmed misroute may mean another solicitation's fetched files landed in the wrong project folder. **2026-08-22 produced documentation only — one commit (`50cfb95`), no code change — but it promoted that misroute from suspicion to a confirmed second occurrence.** An identical-subject copy arrived 14:34:14Z from `ogreen@spectrumsi.com` (the 08-21T18:26:30Z original came from `kgates@spectrumsi.com`) and matched the same wrong slug again, so two misfiled `.eml`/`.email.pdf` pairs now sit in `USAF-B1947-Replace-Lights-ShawAFB/0.RFP/Correspondences/`; meanwhile a differently-worded email on the same opportunity (`DB Replace Chiller B0210-Hurlburt Field, FL`, 08-21T19:29:17Z) correctly auto-staged as a brand-new project (`db_replace_chiller_b0210_hurlburt_field_55099a3d`), confirming a real Hurlburt Field, FL chiller job with no connection to the Shaw AFB, SC lights job. The **mechanism is still unidentified** — the iteration exhausted its budget before tracing which routing branch returned `matched`, and an earlier guess that session (`same_prime`/name-similarity, inferred from a singleton repro) was corrected twice on review and must not be reused; the trace needs redoing against the real project + alias list and `graph_inbox.py`'s full `_process_one_message` flow, not a partial synthetic repro. The live-data repair is still outstanding independent of mechanism. The same window hit the sibling-batch duplicate-staging gap (`_hold_for_review`'s `projects` arg is live projects only — re-confirmed by reading `intake_staging.py`) on **two** more opportunities, each staged twice under the same kgates→ogreen re-forward pattern already documented for the amendment-duplicate-comment class: the chiller bid invite (`..._6a1e10a8` 08-21T18:16:54Z / `..._ff1d7cc3` 08-22T14:34:44Z) and a MacDill AFB SE Shop and Storage Facility invitation (`..._ed08aa84` 08-21T20:31:19Z / `..._50f01a7c` 08-22T14:32:19Z), producing four independent `needs_review` identity cards mutually invisible exactly as that entry's root-cause analysis predicted — queue-only, with an operator note to treat each pair as one opportunity rather than four. Neither 2026-08-23 nor the first half of 08-24 produced a commit here — and then **2026-08-24 became the busiest day in weeks, ~41 commits across four threads.** (1) **Stash recovery** (`24616de`): the pre-push CI gate's 2026-08-12 stash-pop conflict had orphaned ~838 lines, and a line-level audit found ~457 of its 512 distinctive added lines never landed and were never re-implemented — three-way merged back across 14 days of main evolution: the drawing-feedback Accept/Reject loop end to end (those buttons had rendered **dead** on main since the stash), server-side verdict annotation (`_annotate_drawing_feedback`), stale-mount-safe support-file resolution (`_resolve_live_summary_dir`), inline cross-project bias-corpus refresh per verdict (`refresh_aggregate_from_project_roots`; the old CLI refresh scanned one wrong directory and found zero projects, and `discover_feedback_files` is now recursive), manual drawing-add (`force_drawing_matches` override + schema/KNOWN_KEYS + `_overlay_manual_drawing_matches` + per-section UI + the restored `main.py` call site, whose removal in `423ada5` had only ever been needed because the stash held the implementation), building-code-prefixed sheet IDs in `riser_diagram_extractor` (Lackland `D4-M-604`), `path_config.strip_onedrive_dup` handling the File Provider's bare `" 2"` split-domain suffix (not only the classic `(2)` form), and the SAM.gov opportunity link in the project hero (the server had shipped `detail.sam_opportunity_url` for weeks with nothing rendering it). Deliberately not recovered as superseded: `main.py`'s (basename,size) dedup removal and the stash's vision-QC Solicitation-row filter (a refined `quoted_text`-gated version is the live WIP in the working tree). Follow-on rounds made `_overlay_manual_drawing_matches` idempotent and self-cleaning against the process-lifetime `_safe_read_json` cache (it strips ALL prior operator-added hits, un-moves rows whose only evidence was operator-supplied, then re-applies from scratch; the call site runs it even on an empty override so a clear actually cleans up), consolidated legacy `drawing_matches` rows into `top_sheet_hits` (a synthetic-only list was hiding every organic match), stopped `_annotate_drawing_feedback` early-returning on an empty store (removing the LAST verdict must still stamp `""` over injected ones), unioned manual Add with the section's already-saved sheets (the override endpoint replaces the whole key, so a second Add silently discarded the first), and guarded non-list `sheet_ids` from operator-posted JSON. (2) **Dashboard override editor Graph write-through** (`7ac1a58`..`1f15c31`, read side `2527b4a`) — one of the largest remaining holes in slice 10's coverage: for Graph-enabled roots `_handle_override_post` and `_load_project_override_payload` route all I/O through the GraphCache mirror, with `paths["override_path"]` kept as a never-I/O'd tree-path VALUE (matching `_build_slug_index`'s contract). Reads are **index-aware** (`_override_graph_read`, mirroring `find_override_file`'s probe order) so the merge base `resolve()`s an override the delta index knows but the mirror hasn't materialized — otherwise a save merges against `{}` and clobbers remote fields. `GraphUploadPending` is **success-with-warning**: the mirror copy the pipeline reads is updated and the outbox record is durable, but **nothing drains the outbox automatically** (`retry_pending_uploads` still has no production caller), so the message says re-save rather than promising a background retry. `RemoteConflict` is a 409 — the merge base was stale by definition, so **every** pending record for the file is withdrawn via `supersede_pending_uploads` (cancelling only the current payload's hash left an older save latched and livelocked `sync()`'s `remote_changed_while_pending_upload`), the mirror is rolled back to its pre-save bytes via `_atomic_write_bytes` (the pipeline reads that file concurrently), and a rollback I/O failure is surfaced in the 409 rather than swallowed; `FileNotFoundError` is the only "absent" signal, so a transient `OSError` can't make the rollback unlink the last known override. Superseding happens only AFTER a confirmed put (before it, a pre-enqueue failure permanently lost the prior queued edit; after a `GraphUploadPending` it would withdraw the save's own record). Clearing writes an empty `{}` tombstone through the same put — the write-through layer deliberately has no delete — whenever the index knows the file OR mirror bytes exist, and `load_project_overrides` treats `{}` as no-overrides so "Override in use" clears properly. `path_config.graph_relative_path_for` is purely lexical (no `Path.resolve()`, since it runs exactly when the mount may be wedged), and a process-wide `_OVERRIDE_SAVE_LOCK` serializes the whole read-merge-push critical section. It shipped through **eight Codex pre-push rounds**, each finding something real (including two rounds of the code simply overclaiming in its own warning messages and docstrings); rounds 1–7 fixed, round 8's two residual compound-failure windows queued. Tests: `tests/test_dashboard_override_graph_write.py` (30), `tests/test_project_overrides_graph_mirror.py`. (3) **Due-date extraction applied** (`1f9f9fe`, `5ff522f`, `ba87b84` + rounds 2–4) — the class queued and re-queued since item #25 under the standing do-not-auto-apply rule, applied in an attended session because the miss was two days out. Stennis Hall Amd 01 ("Amendment 01 extends bid date to the morning of 9/2. We respectfully request all pricing and proposals no later than COB 9/1") carries no `from X to Y` phrasing, so `_superseding_to_date` never fired and the only `_DUE_TRIGGER` hit was the BuildingConnected auto-footer's superseded "Bid Due: August 27, 2026" — `extract_due_date` returned the stale 8/27 and `extract_sub_due_date` nothing. New `_EXTEND_TO_DATE` (explicit change verb + bid/due date noun + "to", sentence-bounded, no `from` required) is scanned FIRST and outranks any trigger-scan date in the same email, with RFI/Q&A/site-visit wording excluded from the span (Columbus B995's "Extend RFI due date from 11 May to 10 June" still yields the solicitation date); `_SUB_DUE_TRIGGER` gained the prime-ask shapes (`request/submit … all pricing and proposals … no later than`, and separately `asking for proposals … no later than` for NAVFAC NAS H140/Gilbane, where the prime's NLT was the binding sub deadline); `_window_date_iso` takes the **nearest** date in the window across full, yearless month-name, and (new) yearless numeric `m/d` forms with sent-date year inference, because form-priority ordering returned the stale full-form footer date sitting in the same window as the operative bare `9/1`. Verified against the real saved `.eml`: 2026-09-02 / 2026-09-01. Rounds 2–4 added month-abbreviation lookbehinds to the clause splitter ("due date to Sept. 2, 2026" keeps its date while "determined. Site visit 9/2" still splits), a semicolon clause boundary, span marking so a TBD extension can't be rescanned with an unbounded window, and a government-subject guard so "Amendment 0002 requests all proposals…" stays a government date; bare imperatives ("Submit proposals no later than…") no longer fire the prime-ask branch. Round 5's six residuals were **queued rather than fixed inline** — notably that rounds 3 and 5 make lexically contradictory demands about that guard, needing a smarter subject resolver or acceptance of one miss class, not another regex. (4) **False bid withdrawal from mail-security rewriting** (`39bfdca`, `e81a13d`): Barracuda link-protect rewrote a BuildingConnected invite's Bidding / Not Bidding / Not Sure button hrefs to `linkprotect.cudasvc.com/url?a=<percent-encoded goto link>`, dropping the `state=` response marker the CTA strip anchored on, so the bare "Not Bidding" label matched `_BID_WITHDRAWAL_RE` and flipped an active prime (HI MATOC / Absher) to withdrawn. The strip now also anchors on the `buildingconnected.com` domain (literal through percent-encoding), narrowed on review to the `/goto/` CTA path shape so genuine withdrawal prose followed by an ordinary project link stays detectable; the frozen `bid_withdrawn` flag was healed out of hi_matoc's source manifest and pushed back through GraphCache. Also 08-24: silent data loss fixed in the due-date pill editor (Enter and outside-click, `f07dba3`), `retire_duplicate`'s Planner/calendar cleanup made reliable (`0144b22`), a 404 on the Planner task lookup treated as no-thread in the comments read path (`22c4597`, write path unchanged), and `_requeue_failed_project_snapshot` reverting a transiently-failed project's entry before the end-of-poll save so the "will retry" promise is actually kept (non-transient crashes keep the old no-requeue behavior; the one-shot full-refresh path alerts instead, since nothing requeues it). **The sticky-logger-context bleed recurred a fourth time** (`e309324`, auto-applied): `_hydrate_graph_output_dir()`'s three warn `log()` calls relied on sticky context, so under the watch loop's parallel workers a concurrent project's `mark_runtime()` could overwrite the slug mid-pass — confirmed live, an H140 riser-diagram hydration warn tagged `stennis_hall_renovations_keesler_afb_ms`. Four call sites have now been patched one at a time (`faeb3c4`/`bc74454`/`6a747c5`/`e309324`) and the durable fix — scoping or clearing the logger context wholesale — is still not in. Newly queued 08-24/25: item #68 (TaskGoneError, renumbered from the stash), #69 (D4-/D5- prefixed sheet IDs colliding in page-map dedup), #70 (email-parser findings), the round-5 residuals, the **intake OneDrive-only save gap** (intake writes matched-email artifacts only to the CloudStorage tree, so the Graph-backed pipeline can't see an amendment until OneDrive uploads — Stennis needed a manual `GraphCache.put()` of four files before reprocessing ingested anything), a **portal Chrome CDP failure** (`com.rfpautomation.portalchrome`, `:9223` — every BuildingConnected fetch failing with `Browser.setDownloadBehavior: Browser context management is not supported` from inside Playwright's own `connect_over_cdp()`; operator action, not a code fix), another sibling-staged-batch pair (JBC MACC), and a `resolve_category_keys` transient-503 recurrence. Process drift worth flagging: several of the day's pushes used `--no-verify` because the pre-push hook has been timing out fail-open and colliding with the concurrent SENTRY loop's staging. Working tree now carries a second uncommitted body of work beside the parked vision-QC filter: a proposal-artifact-consistency plan (`docs/plans/2026-08-24-proposal-artifact-consistency.md`) and its implementation — an `[artifacts]` table in `matoc.toml` pinning the approved proposal/workbook (relative, inside the project, extension-checked; unconfigured projects keep newest-file discovery only on a unique nanosecond timestamp) and pricing sidecars at schema v2 carrying their source workbook's SHA-256, with readers rejecting a missing or mismatched digest. **2026-08-25 produced no code commits** — all five commits were `SENTRY_IMPROVEMENTS.md` recurrence logs. The portalchrome CDP failure reached an **eighth** consecutive window unrestarted (`grep -c setDownloadBehavior watcher.log` = 248; same portalchrome Chrome, PID 1946, up continuously since 2026-08-15), with every affected email re-verified as correctly routed and low-impact: CTC Propulsion Systems Building Addendum 1 (undecided, so the watcher's full-rerun run-type is correct), FIWA Alert Facility Addendum #06 REV 01 (`no_bid`, archived, Planner-closed 08-24), and Visiting Quarters JBSA Lackland Amendment 5 (`bid`/`ready_to_submit`, light-touch amendment path; a pure-function repro confirms `extract_due_date()` already returns the correct `2026-09-08` from an unconflicted body with no competing stale footer). The latter two each arrived a second time as a `kgates`↔`ogreen` re-forward carrying a distinct `Message-ID`, filing as a separate `..._2.eml` correspondence rather than deduping as a thread reply — but both are `matched` against existing projects, so this is **not** the sibling-staged-batch duplicate-card class, which only affects unmatched intake staging. Portal-fetch failure stays cosmetic in each case (the forwarded mail carries no attachment either, so nothing is lost, just not mirrored from BuildingConnected). The RHV06 stale-Solicitation vision-QC false positive recurred twice in a single window (two `visual_qc.json` generations either side of an auto-correct pass, both carrying the identical blocker), logged without re-queuing. The same report surfaced one genuinely new finding the loop deliberately did **not** chase: a **$0.03 Grand Total mismatch** ($98,390.39 shown vs $98,390.42 expected) — pricing code is queue-only under the standing hard rule, and the operator already had unstaged WIP across exactly those files, so touching them would have risked clobbering real edits. Two other blockers in that report (`dashboard_worklist` "STATUS COLUMN unknown" + templater-leak claims) were matched to the already-documented item #60/#61 registry-write-race / vision-model-invention pattern and not reopened; two warnings (a BBCH primes-table duplicate, a possibly-cut-off §1.6 Submittal Review Panel) were left unchased for budget and noted in case they recur. **The uncommitted working tree is now the fix for that penny drift and has grown well past the 08-24 description:** `pricing_engine.compute_clin_totals` reworked onto `Decimal`/`ROUND_HALF_UP` so currency rounds exactly like Excel's `ROUND(value, 2)` (removing the binary-float artifact), `cyber_engine/pricing_sidecar.py` holding schema-v2 totals sidecars that load only when their SHA-256 matches the exact workbook bytes, `cyber_engine/proposal_price_sync.py` plus a `scripts/sync_cyber_proposal_prices.py` CLI (fail-closed and dry-run by default — exact CLIN match and a single current-engine pricing table required, a recovery copy written, non-price proposal content and formatting preserved, the proposal atomically replaced with cent-accurate CLIN and grand-total values), and a `submission_gate.py` hook running that same dry-run validation inside the dashboard readiness gate, so price drift or an invalid binding blocks `ready_to_submit` while the readiness check itself never edits a document — all of it gated on a project opting in through `matoc.toml`'s `[artifacts]` table, with unconfigured projects keeping newest-file discovery on a unique timestamp. New tests alongside it: `test_pricing_engine_rounding.py`, `test_cyber_engine_proposal_price_sync.py`, `test_cyber_proposals_artifacts.py`. The parked vision-QC Solicitation filter also advanced in-tree to carry round 8's candidate fix — the pricing / grand-total exclusion, so instruction 1's compound "multiple empty panels" BLOCKER can't silently swallow a real empty-pricing defect — while its two other round-8 gaps (the `Finding.location` bypass and the legitimate "Project Info panel failed to render" claim) stay open, and the anchor-phrase-narrowing direction change still stands over adding one more keyword per round. **2026-08-26 produced no code commits either** — five more `SENTRY_IMPROVEMENTS.md` recurrence logs — but the uncommitted tree gained a real new fix found that day: `process_project()` was calling `pipeline_clin_costs` without `inline_cyber_clauses` (silently dropping the DHA-FE deliverable line items `build_pricing_workbook` adds to the Design phase) and without any project/location context (so the rollup used generic `DEFAULT_TRAVEL_RATES` instead of the project's real GSA per-diem location), understating both the Design and Build CLINs on the Ft Sam Lab Exhaust Fan amendment; the same trace found five `pricing_builder` travel-cost call sites hardcoding `flights=0` instead of calling the `_implied_flights(hotel, car)` helper that exists for exactly that (warranty branch uses `trips=hotel`, since each hotel-day there is a separate visit; `_implied_flights`' own docstring already cited a prior $1,600 miss from this class). **No customer-facing document was ever affected** — `pipeline_clin_costs` is an internal cross-check and `main.py` always overrides the proposal cover with the workbook's own SUMPRODUCT values — so this is an internal-consistency fix, not a delivered-pricing correction. The same tree carries the **fifth** sticky-logger-context call-site patch (`run_monitor()`'s pending-intake resolution line now passes `project_slug=""`/`stage="inbox_ingest"`, pinned by `tests/test_main_pending_intake_log_context.py`) — five call sites patched one at a time now (`faeb3c4`/`bc74454`/`6a747c5`/`e309324` + this one), durable fix still not in — plus a `--confirm-scope-matches-workbook` flag now mandatory on `scripts/rebuild_pricing_sidecars.py`, which computes from current scope rather than workbook cells and must not be run after manual workbook-only edits. 2026-08-27 was log-only overnight and then, in a long attended daytime session, the busiest code day since 08-24 — 16 commits across five threads, detailed after the overnight findings. Overnight first: new item **#72**: a `FW: [EXTERNAL] - Ft. Sam - Replace Fire Alarm` re-forward (2026-08-27T00:18:13Z) staged as a fresh `needs_review` card even though `Ft_Sam_Houston_TX-METC_Replace_FireAlarm_B1364` records the byte-identical `original_subject` and is already live and promoted; whether the batch carries the same PIID could not be confirmed from pure functions because the staging batch sits on the OneDrive `Scratch RFP` mount (not a Graph-backed root, unreachable from that iteration), so the proposal is operator-side — compare the batch's top-3 match candidates against the live project before deciding create-vs-merge — with no code fix until it's known whether `match_project`/`_build_solicitation_index` was even given a chance to match. Do not confuse it with `NEW_AMENDMENT_01_Ft_Sam_Lab_Exhaust_Fan_etc`, a confirmed genuinely distinct RCR11 exhaust-fan task order at the same installation. The **sibling-staged-batch gap generalized** on 08-26: JBC MACC took a *third* independent `staged_pending` slug for one opportunity, this time under a different subject entirely (site-visit photos, not the bid invite), proving the gap isn't confined to identical-subject re-forwards; and the Ft Sam amendment staged three times (kgates 08-25, ogreen 08-25, ogreen 08-27 — the latter two both resolving `new_project:` against the same slug at *resolution* time despite staging as independent cards) with a fourth resend 26 minutes later correctly hitting `skipped_duplicate`, so dedup is inconsistent even within one opportunity depending on staging-batch timing relative to the sol-index rebuild. Both remain queue-only under the existing proposed fix (a cross-batch `all_keys` check before `_hold_for_review`). The **grand-total rounding class recurred on a second project** (NEW_AMENDMENT_01_Ft_Sam, `visual_qc.md` 2026-08-27T02:37:50Z: `proposal_docx` + two `pricing_xlsx` BLOCKERs all quoting `$100,879` against `expected_facts.grand_total_usd = 100879.02` — a 2-cent delta matching RHV06's 3-cent one), logged as a corroborating data point and explicitly not touched, since pricing code is queue-only and the operator's own rounding fix is unstaged in exactly those files. Portalchrome's CDP failure hit **windows 9 and 10** still unrestarted (`grep -c setDownloadBehavior watcher.log` 523 at window 9; same Chrome, PID 1946, up since 2026-08-15), both recurrences re-verified as correctly routed and cosmetic. Item **#71** was reviewed and closed the day it appeared: an `mrr_vii` Graph batch-sync read timeout (30s) is the designed degrade path — `_build_site_cache_map()` catches it at `warn`, the site maps to `None` for the poll, and `_snapshot_builder_for_project()` preserves an already-Graph-backed project's `previous_snapshot` rather than doing a local walk that would read as "every remote-only file vanished"; no crash, no data loss, self-heals next poll. The benign 404 hydration-probe pattern logged three more recurrences (Danbury CT and Ft. Wainwright FAS on 08-26, Ft Sam on 08-27), each a genuine first-ever deliverable generation, still not worth a suppressor. **The 08-27 daytime session then produced five threads of real code.** (1) **Graph-native project rename** (`11e7c06`..`32c8aad`): the dashboard's rename endpoint had been running the LOCAL `rename_project_folder` for every project — an `os.rename` against the OneDrive tree, which ENOENTs for Graph-backed roots whose local mounts are empty shells (live failure that morning on `NEW_AMENDMENT_01_Ft_Sam_Lab_Exhaust_Fan_etc`). New `GraphCache.rename_entry` renames ONE index entry and moves its mirror path; because index paths are *derived* from the parent/name ancestry chain, a folder rename re-derives every descendant path with no per-descendant work and the mirror move preserves cached bytes. `project_rename.rename_project_folder_graph` renames the SharePoint folder server-side (`graph_rename.rename_project_folder_remote` — built 2026-08-11, wired only now), follows with the mirror/index rename, then runs the same bookkeeping as the local flow but against the MIRROR (intake-flag clear + push, `migrate_slug_everywhere`, artifact renames local + best-effort remote per-file, `project_detail` re-key + push, drop-folder migration), with `_handle_project_rename_folder` branching on `graph_site_key_for_root` + `graph_backend_roots`. Seven review rounds, each fixed test-first before the next: the mirror moves BEFORE the index name is committed (a failed `os.rename` had left the index pointing at a path with no bytes) and an index-write failure rolls the move back; the remote loop renames EVERY index row carrying an old basename (identical generated filenames can exist in more than one subdir) plus the `.pipeline_hash` sidecars, so old-named copies can't reappear on sync; the folder is resolved through `graph_files.get_item_by_path` anchored at the allow-listed `root_item_id`, **not** `graph_rename`'s drive-root-relative resolve, which renames the wrong item (or 404s) for a Graph root that is a subfolder of its drive (`ssi_fileshare`), and a missing folder is a clean error rather than a rename attempt; collision maps on Graph's stable `nameAlreadyExists` code only, never a `'(409'` substring that could misclassify unrelated failures; an occupied target mirror path is rejected even when the SOURCE bytes are absent (occupied target always means other content lives at that name); `backups/` rows are excluded from the remote rename to match `rename_proposal_artifacts`' local exclusion; the artifact loop passes `allow_existing_target=True` because that function moves the mirror file FIRST, so the follow-up index rekey always saw the target occupied and raised — the swallowed error left the index on the old basename while mirror and SharePoint carried the new one — with the strict default preserving the foreign-content collision contract everywhere else; a failed mirror rename falls back to bookkeeping against the still-OLD-named mirror dir (clearing the intake flag *there* matters, or the watcher's auto-rename undoes the operator's name next poll), pushes to NEW remote paths, reports `mirror_renamed=False`, and returns `status='renamed'` with a warning rather than reading as a clean success, since SharePoint IS renamed and that isn't undone; `_clear_intake_rename_flag` takes an explicit `alias_slug` so that fallback can't derive a stale `old_name -> old_slug` alias off the old dir name; and when the index knows the project but the mirror never materialized, the intake marker and `project_detail` files are hydrated via `cache.resolve()` before bookkeeping (it had silently no-oped, leaving the remote `.intake.json` at `needs_rename=true` and the detail on the old slug), with the degraded-state warning no longer advising an impossible re-run. Live rename verified end-to-end. Round 8's two findings were **queued rather than fixed**: remote artifact renames are driven by `rename_proposal_artifacts` finding MATERIALIZED mirror files, so an evicted artifact keeps its old SharePoint name (the set should come from the index instead), and `migrate_slug_everywhere` isn't failure-isolated, so a real state-file error surfaces as HTTP 500 *after* SharePoint is already renamed — exact parity with the long-standing LOCAL flow, so it should be wrapped for both flows in one pass, not forked. (2) **Four pricing-mirror bugs plus the vision-QC currency false positive** (`032769f`) — this lands the 08-26 finding that had been sitting uncommitted, and it reclassifies the recurring "grand total mismatch" BLOCKERs. `compute_clin_costs_from_pipeline`/`compute_clin_total_costs` (the Python mirror of the workbook's Excel formulas) diverged from the real generated workbook on Ft Sam Lab Exhaust Fan's amendment repricing: DHA-FE deliverable hours were never added to design-phase SCE hours; per-system/design/warranty travel always seeded 0 implied flights instead of deriving them from hotel/car days; MGMT and warranty travel used seeded hotel/car day counts as literal values instead of `CEILING(travel hours/8, 1)`, the workbook's own row formula — undercounting MGMT travel by 2 days on every Build/Base CLIN and warranty hotel/per-diem/rental-car cost on every system whose seeded trip count wasn't already on an 8-hr/day ratio to its own hours (Fire Alarm: 64 warranty hours seeded 4 trips, not `CEILING(64/8)=8`), with Flights deliberately left on the seeded literal since the workbook never turns Flights into a formula; and travel-rate resolution was skipped when only `overrides.force_cover_location` was supplied, silently ignoring an explicit operator override. Separately, `vision_qc_checks._format_expected_facts_for_prompt` rendered grand totals to 2 decimals while the rendered proposal cover shows whole dollars, so an **exactly-correct** total was flagged as a price mismatch on every artifact — meaning the $0.03 (RHV06) and $0.02 (NEW_AMENDMENT_01_Ft_Sam) deltas the loop had been logging as a corroborated rounding class were a QC-side formatting artifact, not delivered-price error. Fixed by calling `proposal_generator._format_currency` directly rather than reimplementing its rounding; an intermediate attempt hand-rolled round-half-away-from-zero for the `.50` boundary and merely traded one mismatch for another, since `_format_currency` uses Python's default round-half-to-even. Two Codex rounds: round 1 found the undercounting, round 2 caught the fix wrongly deriving warranty flights from the recalculated days and inflating them past the workbook's own value. (3) **Name-at-creation for intake-review Create Project** (`3760e36`): the held-batch card's Create Project button now prompts for the folder name, pre-filled with a readable cleaned-subject suggestion (`list_held_batches` carries `suggested_name`); whatever the operator leaves in the box becomes the folder name verbatim via `sanitize_folder_name`, and an operator-chosen name is never overwritten by the watcher's Customer-Location-Description auto-rename (`needs_rename` stays unset). Guardrails: typed names and the suggestion are byte-capped at 180 below the filesystem component limit, a name that sanitizes or slugifies to nothing is rejected at decision time, a create-name matching an existing project (slug or on-disk folder) re-holds the batch with a visible `decision_error` instead of scaffolding over it as if new, and a named create outranks a late-arriving automatic subject/key match so the batch never silently merges into that match while the UI promised a new project (the dedup pass still flags real same-PIID pairs afterward). (4) **Local vision fallback for CUI-gated cover review** (design `5275809`, implementation `b66fa1a`): Ft Sam Houston USAISR sat with an empty `ai_cover_review` and `needs_rename` stuck true *forever* because its ProjNet RFI export carries genuine CUI banner markings, correctly blocking cloud AI with no fallback — unlike `amendment_review.py`/`chat_assistant.py`, which already route to a local model on the same gate. Adds `LocalEnhancer.review_cover_page_vision` (qwen2.5vl:72b via Ollama, reusing the cloud path's `COVER_REVIEW_SCHEMA` through Ollama's `format` field) and `ai_review.review_cover_page_local`, wired into `main.py`'s cover-review block behind `_should_use_local_cover_review()`, which fires only when the CUI gate *specifically* (not `RFP_AI_REVIEW`/`--use-openai`) blocked cloud AI; an independent kill switch `RFP_LOCAL_LLM_COVER_REVIEW_ENABLED` defaults to following `RFP_LOCAL_LLM_ENABLED`, so the already-validated amendment/chat local paths are unaffected. (5) **`onedrive_url_for` no longer stats the real OneDrive tree for Graph-backed links** (`02e3f34`): the Planner-card attachment fix (`real_project_root` translation in `planner_cards._artifact_paths`, which landed alongside unrelated concurrent work in `5275809`) passed real-tree paths straight into `onedrive_url_for()`, which calls `Path.exists()`/`is_dir()` to distinguish a folder link from a file link — exactly the "pure path arithmetic, never I/O'd" contract the Graph migration exists to honor, so the stat could hang the Planner sync and, since the RFP folder likely doesn't exist locally, silently fell through to the file-URL branch instead of a folder listing. It now takes an optional `is_folder` override that skips the probe entirely, passed explicitly by all four Planner-card call sites where the artifact's type is already statically known. Newly queued the same day: the round-8 rename residuals above, and a **`CorruptDownload` finding on the Ft Sam Houston USAISR cluster** — the same underlying project was processed under both its old (`RE_Ft_Sam_USAISR_Fire_Alarm`) and new (`Ft Sam Houston USAISR_Fire_Alarm`) names within one poll cycle, the second logging `Change detected (new)` and reparsing from scratch with a materially different discovery set (460 chunks vs 36), and both runs hit the identical `[...]_Cyber_Proposal_Draft.docx: downloaded 1883490 bytes, expected 1887018` raised inside `write_cyber_proposal()`'s hand-edit check (`backups.file_was_user_edited_graph()`), which unlike item #63's read-only hydration guard is **not** caught gracefully — it propagates to the per-project handler as a hard `ERROR in proposal stage` and aborts proposal generation for that poll (the run continues to validation, so not a full crash like item #64's variant). The "orphaned mirror" framing is explicitly flagged as a hypothesis, not fact: the local OneDrive view shows only the old-named folder while the mirror carries the new one with old-name-prefixed `backups/`, but a Graph write can create a remote folder before the File Provider materializes it, so confirming it needs a live read-only Graph `GET` on both paths, which that iteration didn't do. Queue-only, do-not-auto-apply, potential live-data territory. Portalchrome's CDP failure reached **window 11** unrestarted (four more occurrences, 523+ `setDownloadBehavior` lines, same Chrome PID 1946 up since 2026-08-15), all four re-verified as correctly routed and cosmetic. Process drift continued: three of the day's pushes used `--no-verify` to avoid interleaving with the concurrent SENTRY loop's staging, with the pre-push gate still reviewing the delta. **2026-08-28 produced no code commits at all** — six `SENTRY_IMPROVEMENTS.md` recurrence logs and one new queue entry, the day after the busiest code day in weeks. The new entry is the most consequential: **BBCH DB Replace Chiller B90210, Hurlburt Field FL** — three independent intake events (`db_replace_chiller_b0210_hurlburt_field_55099a3d` staged 08-21, `fw_external_new_message_from_bbch_suppor_9bfdc4c1` 08-27, `fw_external_amendment_0001_extended_prop_5b54661a` 08-28) all trace to one opportunity (PIID FA441726R0035, prime CCI Mechanical via BBCH bid coordination), and `pipeline_logs.jsonl:18458` records the first one resolving 2026-08-24 as `new_project:DB_Replace_Chiller_B0210_Hurlburt_Field_FL` (+4 files) — **yet no such project exists today** under either OneDrive root (`2026 Misc Projects RFP - Documents`, `Scratch RFP`, `_done/`) or anywhere in `monitor_dashboard.json`'s live portfolio, searched by slug, PIID, "chiller", "hurlburt", and "0210"/"90210". Three unconfirmable explanations (a Graph-backend write gap on the `misc` root or a crash between resolve and folder creation; a `_poll_intake_renames()` rename to something carrying none of the searched keywords; or an operator delete/merge), so the proposal is attended-only: confirm via `GraphCache` for the `misc` root whether the project is reachable at all, treat a genuine absence as a live-data-loss incident and re-derive from the three batches' combined files rather than letting the identity gate spawn a fourth copy, and merge rather than create if it is found. One incidental lesson recorded with it — that log line's own `project_slug` field reads `rhv06_...`, the **sixth** sighting of the sticky-logger-context bleed, so the message text is what to trust, not the field. The **sibling-staged-batch gap** took a third card for the separate B90370 Dorm Chiller/Cooling Tower opportunity, and this one is not a harmless re-forward like the prior pair: it is Addendum 03 carrying As-Built drawings and a sub-bid deadline extended to noon EST 2026-09-10, so real perishable content goes unseen if the operator resolves one of the three mutually-invisible cards without knowing the others exist. **Portalchrome's CDP failure reached windows 12, 13, and 14** (same Chrome, PID 1946, up since 2026-08-15), nine events across the three, every one re-verified as correctly routed with a cosmetic portal-fetch failure — including a useful confirmation that the 08-24 `_EXTEND_TO_DATE` fix still holds: Stennis Hall Amendment 02 arrived with the identical extension shape as Amendment 01 ("extends bid date to the morning of 9/8… all pricing and proposals no later than COB 9/4" against a stale "Bid Due: September 1, 2026" footer) and a pure-function repro returns the correct 2026-09-08 / 2026-09-04. The `dashboard_worklist` vision-QC false positive got a **second** data point (RHV06's `visual_qc.json` quoting a duplicate project row `031012` that matches nothing in the 255-project live record set, exactly as `030310` came up empty on 08-27), strengthening but not confirming the screenshot/hallucination hypothesis. The **grand-total rounding class recurred a third time in a materially different shape**: a cross-doc `ai_review` CLIN/Total reconciliation ERROR on RHV06 with a **$1 whole-dollar** delta (Design $28,030 + Build $70,361 = $98,391 against the docx's stated $98,390), not the cents-level artifact the 08-27 `_format_expected_facts_for_prompt` fix explained away — a whole-dollar gap points at the Design+Build sum carrying different intermediate roundings than the docx's own Total field, plausibly a distinct bug in the same area, and it stays queue-only under the pricing hard rule with the operator's rounding WIP still unstaged in exactly those files. Item #71 logged two more recurrences (`umcs_v` this time, `ConnectionResetError` then a read timeout), still the designed transient degrade path with no code change. 2026-08-29 broke the log-only streak with a single contained fix (`e1d900d`, plus `3dbfd7d` logging it): `scripts/generate_health_snapshot.py`'s `_operational_cautions_from_dashboard()` filtered the **full** project list while `dashboard_site.py` scopes `payload["counts"]["operational_cautions"]` to `active_projects` (archived, decided bid/no_bid, and ready_to_submit excluded), so a live snapshot headlined "Operational cautions: 0" and then listed three archived pass-with-exceptions projects (Tinker AFB BACH, NAVFAC-CUI Beaufort P475, USACE Dyess AFB) right underneath. `scripts/generate_daily_ops_report.py` already carried the identical `active_projects` filter for its own `review_buckets` — with a comment naming this exact bug class — so the fix aligns the third aggregator rather than introducing a new rule; **operator-report consistency only, no pipeline behavior change**, pinned by a new `tests/test_generate_health_snapshot.py`. The overnight window into 2026-08-30 was then completely quiet: roughly a dozen consecutive SENTRY iterations returning "clean — no signal" or `auto-applied=0 queued=0`, including a deep scan that reviewed all three aggregators (systemic report clean, health snapshot idle/clean, daily ops numbers at 253 projects with steady-state queue counts) and found no anomaly, so no queue entry and no recurrence log. **2026-08-30 and 08-31 produced no code either** — two commits, both `SENTRY_IMPROVEMENTS.md` recurrence logs, so `e1d900d` is still the newest code change in the tree. Portalchrome's CDP failure reached **window 15** unrestarted, and it doubles as a control: it fired on a *second, distinct* re-forward of Stennis Hall Amendment 02 — the same amendment as window 13, but from `ogreen@spectrumsi.com` rather than `kgates@spectrumsi.com` and with its own `Message-ID`, so it filed correctly as a separate `_2.eml` rather than deduping as a thread reply (same non-dedup pattern already documented on 08-25, and again **not** the sibling-staged-batch class, since this is `matched` against a live project). Step-4b re-verification was clean on every axis: correct existing project (not the unrelated `keesler_afb_repair_jones_hall_project` misroute of 2026-08-05), `extract_due_date`/`extract_sub_due_date` unchanged at 2026-09-08/2026-09-04 — the 08-24 `_EXTEND_TO_DATE` fix holding on a second independent test — and the project still undecided in `dashboard_triage_state.json`, so the full-rerun run-type (not the locked light-touch path) is correct. Portal-fetch failure cosmetic again: the `.eml` is filed, only the BuildingConnected attachment mirror is missing. No new root cause on the CDP failure itself; the restart recommendation is unactioned across 15 windows. Item #71 logged a fourth recurrence overnight into 08-31 — **two in a single poll** this time, `mrr_vii` and `misc` roots both hitting `Read timed out (read timeout=30)` at `main.py:1245` — same designed degrade path, no live-data damage, no code change. Live state on 2026-08-31: `/healthz` `ok` across every check (`graph_indexes` clean with nothing syncing or unreadable, `project_roots` 0/0, `state_integrity` 3/0), `monitor_payload` 253 projects, watcher runtime "current" on a ~37-hour-old process still running `e1d900d` (both of the day's commits touched only `SENTRY_IMPROVEMENTS.md`, so the source fingerprint never changed and nothing re-exec'd), 5,312 tests collected across 279 files — **and that count only holds with `account_store` on `PYTHONPATH`**, which is how this project binds that dependency (pattern 4 below); a bare `.venv/bin/python -m pytest` drops `tests/test_entra_auth.py` and `tests/test_users.py` on `ModuleNotFoundError` and reports 5,270, which reads as a regression and is not one (the delta over the pushed tree is the still-uncommitted pricing/artifact-consistency work — `pricing_engine`'s `Decimal`/`ROUND_HALF_UP` rework, `pricing_sidecar.py`, `proposal_price_sync.py`, `scripts/sync_cyber_proposal_prices.py`, the `submission_gate.py` hook, and since 08-28 a `graph_cache.py` change with its test — plus the parked vision-QC Solicitation filter and the fifth sticky-logger-context call-site patch) | Production |
| cyber-artifact-gen | BAS→diagram/schematic conversion for proposals | Utility |
| email-processor | Inbound RFI/RFQ/RFP email triage and summarization; product renamed **Transom** on 2026-08-10 (display-name only — the `email-intake` CLI, `email_intake` package, launchd unit names, and every file path are unchanged, as is this registry/directory name); 2026-08-12 gave the dashboard and every authenticated auth page a persistent branded sidebar shell matching SENTRY's and Scribe's left-nav pattern, and replaced its hand-rolled component CSS with the shared design-system `.badge`/`.btn`/`.toast`/`table.data` vocabulary; 2026-08-13 added `email_dedup.py` — `Message-ID` (content-hash fallback) checked against the processed-emails index *before* any Claude call, so an exact re-upload costs nothing, plus a merge pass so a re-receipt enriches the existing opportunity instead of overwriting it with a thin follow-up; **2026-08-14 opened a Graph/SharePoint migration of its own** (`docs/superpowers/specs/2026-08-14-graph-sharepoint-migration-design.md`, spec round 4, closed to further abstract review) to move the vault, inbox, and PP source off the OneDrive mount that was deadlocking both LaunchAgents with `Errno 11 Resource deadlock avoided` — **this does not reopen the locked "no Graph API" decision**, which blocks Graph for *mail ingestion* (`Mail.Read`) only; these are plain SharePoint document-library folders under `Sites.Selected`, and mail content processing stays local. Plan 1 of 3 is merged: a standalone `graph/` module (host resolution, cert-based client-assertion auth, `GraphClient` with retry/backoff, per-root locking, id-keyed local `Cache` mirror with write-ahead crash safety; `push_retry()` matches on **quickXorHash**, the only hash SharePoint/OD4B returns) with **zero wiring into the live pipeline/watcher/webserver**; 2026-08-15 was a correctness pass over it, still unwired — `get_item_by_path()`'s drive-root bootstrap used `/items/root:/{path}` where Graph's real syntax is `/root:/{path}` (would have 404'd on the first real run; caught against Microsoft's docs, not by a test), `push()` now rejects absolute or `..`-bearing relative paths (`cache_dir / "/etc/passwd"` evaluates to `/etc/passwd`, so the existing equality check couldn't catch it), moved-outside-root cleanup cascades to tracked descendants, and `resolve()`/`sync()` no longer hold `root_lock` across network calls per `graph/lock.py`'s own contract — which exposed and closed a concurrent-download tmp-filename collision and a slow-download clobber. Four further concurrency findings (out-of-order delta tokens, resurrect-on-delete, full-resync pruning races, symlink path-confinement) were deliberately left open: none corrupts file content and deployment is single-writer-per-root, though "a later sync self-heals" holds for only three of the four — a resurrected entry survives incremental sync (its tombstone was already consumed and the delta token advanced past it) and needs a full resync to prune — and a proper fix needs a coarser whole-`sync()` lock tracked as a design addition. **Credential choice resolved 2026-08-18 — reuse SENTRY's cert and app registration** (no code impact on Plans 1–2, since auth is Plan 1 code; it clears Plan 3 to go to live credentials). **Plan 2 of 3 merged the same day in 16 commits — the nested-cache retrofit**: `CacheEntry.local_filename` changed from a bare id-stem filename under `cache_dir` to a root-relative POSIX path derived by walking `parent_id` ancestry with on-demand ancestor healing (so derivation never depends on delta batch ordering), plus a per-root naming policy keeping real basenames for app-authored deterministic names (`summary.md`, `email.*`, `*.docx`) and id-stems for everything externally named — required because the flat store is structurally incompatible with `dashboard.py`'s `vault_root.iterdir()`/`sub.glob("*.docx")` and the webserver's `StaticFiles(vault_root)` mount, the blocker recorded 08-17. Write-side primitives for Plan 3 landed with it (`create_folder` w/ 409-adopt, `ensure_remote_dir`, `push_update` w/ If-Match + crash-safe pending retry, write-ahead `move`, `push_tree`). The day's key fix was a data-loss path the spec described and the code never implemented — the "Sync ordering" rule that a local pending write beats a same-cycle incoming delta: `_apply_delta_item` never checked pending state, so a same-batch tombstone for an item whose `push_update` had failed would unlink the local file and drop the entry, destroying never-uploaded edits; closed by re-verifying `_is_pending()` under *each* commit lock (not once up front), extending the guard to `sync()`'s separately-locked out-of-scope cleanup, adding `skip_pending`/`skip_if_pending` to the cascade/folder-registration helpers, having `delete()` report whether it made a real Graph call, and keying same-cycle stale-delta suppression to the remote etag observed via `get_item()` — never id membership alone, never a bare `None == None`. Two `push_tree` sweep bugs fixed too (dot-directory asymmetry could delete remotely what the sweep would never upload; `push_tree("")` built prefix `"/"` and silently no-op'd). Still **zero production wiring** (verified 08-18), so no deployed-cache schema migration is needed; Plan 3 (pipeline/watcher/webserver + PP source) is the remaining work. 590 tests across 38 files, 149 covering `graph/` | Production |
| outlook-followup | "Follow-Up Reminder" Office.js add-in (~1,300 LOC): intended to flag sent mail and remind on no-reply via Outlook flag + To Do task + taskpane dashboard, with Graph reply detection and `roamingSettings` sync. **Graph-backed half is non-functional** — `mailbox.js` passes a callback to the promise-only `Office.auth.getAccessToken`, so `getGraphToken()` never settles; and `storage.addItem()` dedups on `conversationId`, which is `null` at compose time for a brand-new (non-reply) message — replies inherit a real `conversationId` from the thread — so `OnMessageSend` auto-tracking on consecutive new messages overwrites the previous entry | Written, never run — not a stub, but not working either |
| past-performance | SSi past-performance doc search + extraction | v1 |
| project-tracking | Job budget/cost/labor/submittal dashboard; React v2 UI primary. **Sage-only ingestion** as of 2026-08-07 (Phase 3 cutover retired the funding/labor-PDF report pipeline entirely) — Sage 100 Cloud Connector read live is the sole data source, Planner/SharePoint Graph sync optional on top for % Complete and bucket counts, so a `viewer` account can't track jobs of its own (it still sees jobs shared with it — the shared-jobs merge gates on the owner's role, not the recipient's). AR/AP cash position + invoice-level detail; broadened weekly Executing Review, now cache-backed and prewarmed hourly by a fifth LaunchAgent (`com.ssi.project-tracking-exec-sync`); open-PO commitment attributed to phase/CLIN via `pchord.phsnum` (Committed/Remaining columns, unclassified-committed row); EAC worksheet built but flag-hidden; completion source is **job-level, not per-user** as of 2026-08-10 (`shared_job_state` + one-time migration; `/api/jobs/{job}/source` and `/api/manual_pct_complete` write it gated on tracking the job), and nine `cloud_root` chokepoints now degrade gracefully on a stuck OneDrive mount instead of raising — the worst, `fingerprint_inputs()`/`_one_cycle()`, had been crash-looping every 60s poll under `auto_refresh_loop` | v1 |
| project-monitor | Project folder + Outlook email → PM status via entity registers (contracts, mods, POs, invoices, pay apps) | v2 |
| cyber-brain | SSi cyber group knowledge system: Graph ingestion (SharePoint/Planner/Teams/email) → per-project event stream, briefs, cited Q&A | v0.1 |
| daily-summary | Power Automate daily email digest solution | v0 |
| fulcrum-replacement | Offline-first mobile field data collection platform (Fulcrum SaaS replacement) | Design only |
| network-scanner | Active network discovery + BACnet enumeration | v1 |
| ethernet-link-analyzer | Passive LLDP/CDP Ethernet discovery; Pi field appliance w/ touch UI, battery, gated active tests | Phase 4 |
| virtual-devices | BACnet/IP virtual building fleet (76 devices) | v1 |
| digital-twin | DOPPEL — FRCS HVAC plant digital twin + fault injection; selectable twin models (office-building / barracks-cep campus, mutually exclusive, live-switchable from the HMI), electrical model, 65-detector FDD on office-building after the open-fdd parity port (barracks-cep coverage partial) + cross-scope cascade diagnosis; config-driven mode emulates a real site from a Niagara Supervisor backup (via niagara-config, designed-for future third model) — incl. per-detector role catalog + `config coverage` report, fault injection addressed by real equipment id, findings in real config names, `config export-fixtures` labeled diagnosis fixtures, and backup **history replay** (`HistoryReplaySource`, live via `TWIN_HISTORY_REPLAY` or headless via `config replay-backup`); 2026-08-25 added a hand-rolled **DNP3/TCP outstation** (post-2.15, no CHANGELOG entry yet, so the revision number is unchanged) — CRC, link framing, transport segmentation and application layer written from scratch with no DNP3 library dependency, then made model-agnostic so two instances share one wire layer: `twin/dnp3_server.py` for the office-building electrical service entrance (switchgear/SCADA level, sibling of the panel-level read-only electrical Modbus server) with CROB (g12v1) control of breakers, trip-reset and ATS transfer/retransfer, and `campus/dnp3_server.py` for barracks-CEP site distribution with CROB control of the campus L0 breakers and no transfer points (that model has no ATS or generator). Static data only — integrity (Class 0) polls, no event buffers, no unsolicited responses; off unless `TWIN_DNP3_PORT`/`TWIN_CAMPUS_DNP3_PORT` is set, loopback bind by default, frames from any link address other than the configured master dropped. The campus map fixes 23 breaker slots so indices stay stable across barracks counts (absent slots read closed/tripped False with 0 amps; a CROB to one returns status 6 `HARDWARE_ERROR`), reserves ten barracks slots, and caps DNP3 exposure at the first ten to match the campus Modbus cap. Contracts in `docs/DNP3_POINTS.md` / `docs/CAMPUS_DNP3_POINTS.md`, each pinned by its own test module; the electrical model also gained an `ATS.test_mode` commanded load-test latch. 2026-08-26 added the operator-facing half (still post-2.15, still no CHANGELOG entry): a **Campus DNP3 Control card** on `/campus` that opens/closes/resets breakers by issuing real g12v1 SELECT+OPERATE CROBs through a new loopback master (`twin/dnp3_client.py`) against the in-process campus outstation, so the card exercises link framing, transport, and select-before-operate rather than mutating the model directly — `POST /electrical/dnp3/breakers/<id>` (503 when the outstation is disabled, 502 when unreachable) and `GET /electrical/dnp3/card` (live partial, 2s poll, result line kept outside the poll region), placed on `/campus` because `/electrical` redirects there in a model with no office building. `dnp3_client` is deliberately not a general-purpose master (one control per call, no polling, no unsolicited handling) and reuses the outstation's own wire helpers so a single framing/CRC implementation serves both sides. 1,410 tests across 89 files | rev 2.15 |
| pocket-probe | STM32 LLDP/CDP keychain device | Prototype |
| prtg-import | Bulk PRTG device import from CSV | Production |
| kml | KML/topology generation utilities (JBLM) | Utility |
| cert-manager | Employee training cert tracker | v0 |
| project-creation | Post-award Cyber SharePoint and Planner provisioning (Graph app-only auth, SharePoint resolver) | Scaffolding — no CLI run command yet |
| account-store | Shared user account management library | Library |
| ssi-design-system | SSi brand tokens + CSS + doc generation | v0.1 |
| claude-sync | Syncthing conflict resolver for ~/.claude | v1 |
| claude-memory-compiler | Hook-captured Claude conversations → compiled knowledge articles | v0 |
| floor-plan-editor | 2D/3D floor plan editor → HA card export | **Not on this Mac** — see note below |
| niagara-docs | Niagara 4.10/4.15 runtime binary cache + Supervisor backup (dev reference, not a project); also holds the authored `SOP/` library (CAC web access, backup/DR, keyring recovery, Supervisor station migration, FIPS 140-2 setup) — the only part still edited | Stub |
| niagara-llm | CASCADE — external LLM analysis brain for Niagara BAS (oBIX/REST-BQL/SQL); FDD + LLM diagnosis, air-gapped local LLM (Ollama), Supervisor audit CLI, backup assessment; backup parser/classifier extracted to niagara-config (consumed via shims); offline diagnosis scorer (`diag-score` + `FixtureSource`) grades detection against digital-twin's labeled fixtures; dashboard API sends portfolio-baseline security headers (CSP/X-Frame-Options/etc. via `api/security_headers.py`, mirroring project-tracking; HSTS opt-in behind `SECURE_HSTS`) | v2 |
| niagara-config | Shared library: Niagara Supervisor backup (`config.bog`) parser + point→equipment/role semantic classifier; extracted from niagara-llm, consumed by niagara-llm (shims) and digital-twin | Library |
| sanguine | Internal Levels.com-style blood-lab results viewer (PDF/CSV + Apple Health import, optimal vs standard ranges, trends, biomarker detail pages, PhenoAge biological age, vitals, Claude-generated cached explanations) | v1 |
| siem-forwarder | Niagara 4 JACE module forwarding security-relevant BACnet MS/TP wire operations to a SIEM over RFC 5424 syslog/TLS, non-interference design (audit/platform logs deliberately left to Niagara's native remote syslog; `forwardAudit` exists as a config slot but is not acted on). **Design changed shape 2026-08-11 in response to PNNL's "capture all RS-485 traffic" answer:** SDD v1.5 retired ride-along point-COV outright and v1.6 retired alarm forwarding too, leaving the §13 receive-only passive MS/TP listener (second serial port jumpered onto the live trunk, custom frame + APDU decoder, *not* layered on Tridium's driver) as the sole collector; non-interference redefined from "add no polls" to electrical/receive-only invariants plus a still-missing admission-control hook upstream of decoding. v1.7 confirmed `BISerialService` reachability, exclusive port ownership (the two-port jumper is the only route), and the licensing caveat as low-risk; SDD now **v1.8 (draft)** with listener test cases T13–T16. **The SDD split in two on 2026-08-12:** `siemForwarder-SDD.docx` is the customer-facing variant (Sec 11 and Appendices A/B dropped, 12→11 and 13→12 renumbered throughout, Revision History removed), and `siemForwarder-SDD-Internal.docx` keeps Sec 11's findings in the confirmed/verified tense that matches the real skeleton source — the customer copy deliberately reads its findings as preliminary even though the Java skeleton already carries the fixes, a documented choice of tone over strict source-consistency. T12 was also split into a Phase-1-runnable baseline gate plus a new listener-inclusive T17 re-run. `MstpPassiveListener.java` doesn't exist yet and `RideAlongSubscriber.java` is marked obsolete; the repo's own `README.md` still describes the retired design and is stale. Joined by a `siemForwarder-PilotCostProposal-DRAFT.docx` (PNNL, two-phase single-trunk pilot; 12 Aug 2026, 60-day validity, 272–448 hrs / $62,560–$103,040 combined) | Skeleton/design-complete |
| scribe | SSI Scribe — self-hosted AI meeting note taker: Whisper/MLX ASR, pyannote diarization, Ollama gpt-oss:120b summaries (own repo: github.com/ogreen111/scribe); ASR hallucination postfilter hardened 2026-08-10 (periodicity test, known-phrase matching, zero-gap short runs, word-timing-aware prefix stripping) and `SCRIBE_ASR_LANGUAGE` now pins ASR to English so auto-detect stops inventing Japanese; the 2026-08-13 auto-screen-share-detection design was **implemented on 08-14 in 28 commits** — a real MV3 Chrome/Edge extension under `extension/` (background service worker, Meet + Teams content scripts over a shared pure `presence-detect.js`, pure `share-state.js`, a `content-scribe-bridge.js` relay into the SPA, and an options page granting one Scribe origin via `optional_host_permissions`), entirely client-side with no new backend routes or server state; Zoom and Teams *desktop* stay manual-button-only, and the manual **Capture screen** button remains the fallback. About half those commits are review-driven cross-context race fixes (a provably-correct `allowPrompt` flag replacing a prevState heuristic, token-scoping extended to outbound `prompt`/`clear` relays but relaxed for a tokenless `superseded` since the unpacked extension version-skews against the app, `chrome.scripting.executeScript()` fallback for tabs opened before install) | v0.1 |
| scripts | Mount automation + Bash utilities (own repo: github.com/ogreen111/og-scripts, lives at `~/dev/scripts`); since 2026-08-10 also the home of the portfolio's own tooling — `migrate-project.sh`, `refresh-portfolio-docs.sh`, `codex-pre-commit-review.sh`, `install-codex-pre-commit-hook.sh` — moved out of the untracked `~/Documents/dev/scripts` so they are version-controlled and backed up off-machine, with the hook installer re-pointed at `~/dev`; 2026-08-11 added a third hook, `codex-plan-review.sh` (Claude Code `PostToolUse(Write)` review of plan/spec docs), hardened `migrate-project.sh` over seven commits (ditto-and-verify before any `rm -rf`, nested-worktree relocation, push state checked against origin, sub-second mtime fingerprint, ANSI-stripped `brctl` parsing) and a linked-worktree guard in the pre-commit hook, and dev-portfolio untracked its own stale `scripts/migrate-project.sh` so og-scripts is the single owner | Active |

---

Note: this "scripts" registry entry (`~/dev/scripts`, its own `og-scripts`
repo) is unrelated to `~/Documents/dev/scripts/` — dev-portfolio's own
untracked, gitignored local tooling directory (`migrate-project.sh`,
`codex-pre-commit-review.sh`, etc.). They share a name but are different
directories with different origins; the registry entry was never part of
dev-portfolio's own tracked history and needed no relocation.

**`floor-plan-editor` is missing from this Mac (noticed 2026-08-06).** All 30
other registry entries resolve to a real directory under `~/dev/`; this one
resolves to nothing — not `~/dev/floor-plan-editor`, not
`~/Documents/dev/floor-plan-editor`, nowhere else under `~`. It's listed in
`.gitignore` with zero tracked files, so dev-portfolio's own history has no
copy to restore from, and it appears in **none** of the migration batches
documented below — it looks like it was simply never carried across when
everything else moved out of `~/Documents/dev`. Since this machine is the
one that runs behind the Mac Studio, check there (and Time Machine) before
treating it as lost. Left in the registry rather than deleted, because the
registry is the portfolio's source of truth for what *should* exist.

Also present under `~/dev/` but deliberately **not** registry entries:
`sops`, `stream-deck`, and `trim-backup` (untracked, gitignored plain
directories — `stream-deck` is a real, buildable Elgato plugin and is the
strongest candidate for promotion into the registry), plus the empty
`niagara-mcp-integration` directory and the repo's own `deploy/` and
`docs/`.

## Shared Dependencies

- **account-store** → consumed by: rfp-automation, project-tracking, email-processor, past-performance, project-monitor, cert-manager, project-creation, digital-twin (`twin/auth.py`, imported by `twin/web.py` and the admin/session routes)
- **ssi-design-system** → `apps.json` marks six consumers enabled: project-tracking (the v0 pilot), rfp-automation, email-processor, cyber-artifact-gen, digital-twin, and floor-plan-editor. Synced brand bundles verified on disk 2026-08-10 in **all five** enabled consumers that exist — project-tracking (`frontend/src/brand`), rfp-automation (`src/rfp_automation/web/brand`), email-processor (`src/email_intake/static/brand`), cyber-artifact-gen (`brand`), digital-twin (`twin/static/brand`) — plus **scribe** (`src/ssi_scribe/web/brand`), which carries a bundle but has no `apps.json` entry, so it drifts on every rebuild until it's added. (Unrelated: `niagara-llm/brand/` holds CASCADE logo assets, not a design-system bundle — don't mistake it for a consumer.)
  - **`sync.py`'s post-migration breakage is fixed** (2026-08-06). `apps.json`'s `_root` was `/Users/ogreen/Documents/dev` while `sync.py` resolves every target as `_root / name / target`, so a sync run skipped every consumer with "app directory not found"; `_root` is now `/Users/ogreen/dev` and five of the six enabled targets resolve. **`floor-plan-editor` is still the odd one out** — enabled in `apps.json`, but the project has no directory anywhere (see the note above), so it remains the one entry needing a decision.
  - The bundle now includes `interactions.js` (`guardAriaDisabled()` — keyboard-activation guard for `[aria-disabled="true"]` elements, since `pointer-events: none` doesn't stop keyboard activation). It has been synced into all five on-disk consumers; a consumer page must load it and call `SSiInteractions.guardAriaDisabled(document)` for it to do anything.
  - **A branded left-nav sidebar shell is emerging as the portfolio's de-facto app chrome**, though it is a copied pattern rather than anything the bundle ships: rfp-automation (SENTRY) and scribe established it, and on 2026-08-12 email-processor adopted it across its dashboard and all authenticated auth pages, dropping its hand-rolled component CSS for the shared `.badge-*`/`.btn-*`/`.toast--*`/`table.data` classes. Consumers deepening their use of the shared *vocabulary* like this is the design system working as intended; the sidebar *markup* being hand-copied three times over is a candidate for promotion into the bundle.
- **rfp-automation** → consumed by: project-creation (a `[tool.uv.sources]` path dependency alongside account-store, so project-creation needs both siblings checked out)
- **virtual-devices** → pairs with: digital-twin (frcs-digital-twin) for integration testing (see `virtual-devices/INTEGRATION.md`)
- **niagara-config** → consumed by: niagara-llm (via re-export shims), digital-twin (config-driven mode, now including backup history replay — `HistoryReplaySource` reads `niagara_config.backup.csv_history_lookup`'s CSV format)
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

## rfp-automation lives outside this tree

As of 2026-08-05, **rfp-automation is no longer under `~/Documents/dev/`** —
it was relocated in full to `~/dev/rfp-automation` to get it off iCloud
entirely, which makes the `.venv.nosync` workaround below moot for that
project (nothing there is iCloud-synced anymore) — but its venv still uses
the same `.venv → .venv.nosync` symlink layout for consistency with the rest
of the portfolio's tooling. `~/dev` is the separate `dev-portfolio` git repo;
`rfp-automation/` is listed
in its `.gitignore` so the moved project's files (including CUI-bearing
`projects/`) never enter that repo's tracked history. All 8 launchd agents
(dashboard, watcher, sentryloop, logrotate, optimizeloop, plannerchrome,
portalchrome, dashboard-healthcheck) and their `output/live_monitor/` plist
sources were repointed at the new path; `account-store` (a dependency, not
moved at the time) was still referenced from its original
`~/Documents/dev/account-store` absolute path — superseded once
account-store itself moved, see "account-store migrated, all 8 dependents
re-pointed" below. Start sessions for this project from
`~/dev/rfp-automation`, not here.

## niagara-config, niagara-docs, niagara-llm, niagara-mcp-integration live outside this tree

As of 2026-08-05, these four are no longer under `~/Documents/dev/` — moved
to `~/dev/` for the same iCloud reasons as rfp-automation above. All are
listed in `~/dev/.gitignore`. No launchd agents reference any of them (the
`actions.runner.ogreen111-niagara-llm.*` self-hosted CI runner clones from
GitHub, not the local path, so it's unaffected). `niagara-llm`'s server was
stopped and restarted from the new location (still port 8770); its
dependency on `niagara-config` (`pyproject.toml`'s
`niagara-config = { path = "../niagara-config", editable = true }`) is a
relative path that still resolves since both moved as siblings. `git
worktree repair` was run on both `niagara-config` and `niagara-llm` (3
linked worktrees under `niagara-llm/.claude/worktrees/`) to fix the
absolute-path worktree admin links.

Moving `niagara-docs` (134GB) and `niagara-llm` (837MB, several worktrees)
surfaced a real gotcha: **plain `mv` deadlocks on the `rename()` syscall**
for anything under the iCloud-synced `~/Documents/dev`, even when `stat -f`
shows the source and `~/dev` on the same device — iCloud's file-provider
daemon still intercepts and can hang indefinitely. `ditto` (copy via
read/write syscalls, APFS clone-aware so it's still fast) avoids the
coordinator entirely; used for all four moves here, each verified
(file-count diff, git HEAD/status match, or per-file size diff for
niagara-docs) before deleting the source. A pre-existing
`~/Documents/dev/scripts/migrate-project.sh` (built per
`.plans/dev-relocation/`, a broader, partially-executed multi-project
relocation plan authored 2026-08-01 — Batch 0 done, batches 1+ not yet run
at the time) used plain `mv` and would have hit the same deadlock — it was
patched to use `ditto` before running any further batches, and every batch
after this one used the patched script. Also: two stray,
already-hung `mv` background processes (targeting `project-tracking` and,
separately, `niagara-docs`) were found and killed during this session's
move without having touched any data — one predated this session
entirely, the other was this session's own first (later-abandoned) attempt
at `niagara-docs` before switching to `ditto`.

## digital-twin lives outside this tree

As of 2026-08-05, **digital-twin is no longer under `~/Documents/dev/`** —
it was relocated in full (the `frcs-digital-twin/` git repo, plus the
untracked `supporting/` architecture docs) to `~/dev/digital-twin/` via
`ditto`, verified by file-count/size diff and git HEAD/status match against
the Documents copy before deleting the source. `~/dev` is the separate
`dev-portfolio` git repo; `digital-twin/` is listed in its `.gitignore` so
the moved project's files never enter that repo's tracked history. The
`niagara-config` dependency fix mentioned above (`requirements.txt` pinned
to the absolute path `-e /Users/ogreen/dev/niagara-config`) was still
uncommitted in the old Documents copy — carried over to the new location as
uncommitted changes rather than reverted to a relative path, kept absolute
for consistency with how `account-store` is referenced elsewhere in the
portfolio. The `com.ssi.digital-twin` launchd agent (port 8080; not running
at move time) was repointed at the new path. Start sessions for this
project from `~/dev/digital-twin/frcs-digital-twin`, not here.

---

## project-tracking lives outside this tree

As of 2026-08-05, **project-tracking is no longer under `~/Documents/dev/`** —
it was relocated in full to `~/dev/project-tracking` to get it off iCloud
entirely, which makes the `.venv.nosync` workaround below moot for that
project (nothing there is iCloud-synced anymore) — its venv was rebuilt
fresh at the new path rather than moved, but still uses the same
`.venv → .venv.nosync` symlink layout for consistency with the rest of the
portfolio's tooling. `~/dev` is the separate `dev-portfolio` git repo;
`project-tracking/` was already listed in
its `.gitignore` so the moved project's files never enter that repo's tracked
history. All 4 launchd agents (project-tracking, project-tracking-snapshot,
project-tracking-sage-prewarm, project-tracking-exec-report) and their
`~/Library/LaunchAgents/*.plist` sources were repointed at the new path;
`account-store` (a dependency, not moved at the time) was referenced from
its original `~/Documents/dev/account-store` absolute path via a symlink
into the new venv's site-packages per `AGENTS.md`'s setup recipe —
superseded once account-store itself moved; see "account-store migrated,
all 8 dependents re-pointed" below, which recreated this exact symlink
pointing at `~/dev/account-store`. Start sessions for this project from
`~/dev/project-tracking`, not here.

## email-processor lives outside this tree

As of 2026-08-05, **email-processor is no longer under `~/Documents/dev/`** —
it was relocated in full to `~/dev/email-processor` via `ditto`, verified by
byte-level `diff -rq` (18,474 entries, clean) and git HEAD match against the
Documents copy before deleting the source. The repo had uncommitted changes
at move time (`git stash -u`, popped back cleanly at the new location — same
working-tree diff before and after). `~/dev` is the separate `dev-portfolio`
git repo; `email-processor/` is listed in its `.gitignore` so the moved
project's files never enter that repo's tracked history. Both LaunchAgents
(`com.ssi.email-intake.webserver`, `com.ssi.email-intake.watcher`) and
`scripts/webserver-entrypoint.sh`'s working directory were repointed at the
new path.

This was the project noted below as "partially migrated" (`.venv.nosync`
alongside a plain, un-symlinked `.venv`, skipped earlier because its server
was running from `.venv`) — that's now resolved. Moving broke the console
scripts: Python venv entry points (`.venv/bin/email-intake`, etc.) bake in an
absolute shebang to the venv's own interpreter at creation time, so it kept
crash-looping (`Failed to spawn: email-intake ... No such file or
directory`) even after the plist/entrypoint repointing above succeeded.
Fixed by rebuilding the venv fresh at the new path: `uv sync --dev` (plain
`uv sync`, without `--dev`, silently skipped installing the project's own
`email-intake` console script — this project's Makefile always uses `--dev`,
so match it, not the shorter recipe below), then re-editable-installed
`account_store` (`uv pip install --python .venv/bin/python -e
~/Documents/dev/account-store` — not a `pyproject.toml` dependency, so `uv
sync` alone never restores it) from its still-unmoved original location, then
fixed a stray real `.venv` directory left over from an earlier `uv sync` run
back into the intended `.venv → .venv.nosync` symlink. Both LaunchAgents were
bounced (`bootout` + `bootstrap`) and confirmed running with live PIDs
afterward; `make serve`/`make watch-once`/etc. still apply the
`chflags nohidden .venv/lib/python*/site-packages/*.pth` workaround this
project's own Makefile documents, so prefer those over a bare `uv run`. Start
sessions for this project from `~/dev/email-processor`, not here.

## cert-manager lives outside this tree

As of 2026-08-05, **cert-manager is no longer under `~/Documents/dev/`** —
it was relocated in full to `~/dev/cert-manager` via `ditto`, verified by
byte-level `diff -rq` (21,233 entries, clean) and git HEAD match against the
Documents copy before deleting the source. The repo had one uncommitted
change (`CLAUDE.md` doc updates), stashed before the move and popped back
cleanly at the new location. `~/dev` is the separate `dev-portfolio` git
repo; `cert-manager/` is listed in its `.gitignore` so the moved project's
files never enter that repo's tracked history. Both LaunchAgents
(`com.ssi.cert-manager-frontend`, `com.ssi.cert-manager-backend`) were
repointed at the new path.

Same stale-shebang fallout as email-processor above hit `backend/.venv`
(`.venv/bin/uvicorn`'s shebang still pointed at the deleted
`.../Documents/dev/cert-manager/backend/.venv/bin/python3.14`, so the
backend crash-looped even after the plist repointing succeeded) — but this
project isn't part of the `.venv.nosync` convention at all (plain `.venv`,
no `uv`), so the fix was the project's own documented recipe instead:
`rm -rf backend/.venv && cd backend && python3 -m venv .venv &&
.venv/bin/pip install -e ".[dev]"`. `backend/pyproject.toml`'s
`account-store @ file:///Users/ogreen/Documents/dev/account-store`
dependency needed no change at the time — that absolute path was still
correct since account-store hadn't moved yet (superseded once it did; see
"account-store migrated, all 8 dependents re-pointed" below, which fixed
this exact line to `~/dev/account-store`). Both LaunchAgents were bounced (`bootout` +
`bootstrap`) and confirmed live: backend `GET /api/health` → `200
{"status":"ok"}`, frontend → `200`. A `watcher: CERT_ROOT does not exist`
line in the backend log is unrelated to this move — `CERT_ROOT` points into
`~/Library/CloudStorage/OneDrive-...`, not `Documents/dev`, and just wasn't
mounted/synced at the time. Start sessions for this project from
`~/dev/cert-manager`, not here.

## network-scanner lives outside this tree

As of 2026-08-05, **network-scanner is no longer under `~/Documents/dev/`** —
relocated in full to `~/dev/network-scanner` via `ditto` (9,988 entries,
byte-identical, HEAD match). Was checked out on a feature branch
(`inventory-baseline-and-scan-runs`), not `main`, at move time - clean and
fully pushed there too. A pre-existing nested Claude Code worktree at
`.claude/worktrees/hopeful-benz-342a84` (detached HEAD, no uncommitted
changes, commit fully pushed) had to be removed with `git worktree remove`
first - its presence trips `git worktree repair`'s side effect of mutating
that worktree's own `.git` file mid-run, which then fails the script's final
pre-deletion diff check (see the `migrate-project.sh` commit history for the
general writeup). Also cleared 4 stale root-owned `__pycache__/*.pyc` files
(gitignored, safe to delete, blocked `ditto` with "Permission denied") left
over from some earlier process that ran with elevated privileges. The
`com.ssi.network-scanner` LaunchAgent wasn't loaded before the move (reason
unclear) - loaded manually afterward and confirmed serving (`GET /` → 200 on
:8000, via the LaunchAgent's `.venv/bin/python -m uvicorn` invocation - it
doesn't route through a console-script wrapper, so no venv rebuild was
needed for it). `.venv/bin/python` itself is a relative symlink chain
(`python -> python3.14 -> /opt/homebrew/...`), so that invocation form
survived the move intact - but this venv's console-script wrappers
(`.venv/bin/uvicorn`, `.venv/bin/pip`, etc.) still have the same stale
absolute shebang as every other project's here, so don't invoke them
directly; the Port Map's start command below uses the same `python -m`
form as the LaunchAgent for exactly this reason. Start sessions for
this project from `~/dev/network-scanner`, not here.

## past-performance lives outside this tree

As of 2026-08-05, **past-performance is no longer under `~/Documents/dev/`** —
relocated in full to `~/dev/past-performance` via `ditto` (9,694 entries).
Had substantial uncommitted work at move time (an in-progress session-auth
feature - `app/auth.py`, `tests/test_auth.py`, etc., 11 modified + 4
untracked files) plus a stray untracked `.pp_index.sqlite.corrupt-...` debug
artifact - stashed (in two passes; a first `git stash -u` didn't pick up
`.pp_auth/` and a `.bak-orphanfix-...` file for unclear reasons, needed an
explicit pathspec on a second pass) and restored cleanly at the new
location, working tree matching exactly. Same nested-worktree removal as
network-scanner above (`.claude/worktrees/competent-wilson-86dd33`, same
safe-to-remove profile: detached HEAD, clean, fully pushed). Same
stale-shebang fallout as email-processor/cert-manager hit `.venv/bin/uvicorn`
- fixed the same way as cert-manager (plain `python3 -m venv .venv`, no
`uv`/`.venv.nosync` convention here), plus a manual `account_store` editable
reinstall from its still-unmoved original location (also undocumented in
this project's own setup docs, like email-processor). LaunchAgent confirmed
live (`GET /` → 200 on :8767); its startup log's "removed: 29" is normal
reconciliation against the live OneDrive PP folder, unrelated to the move.
Start sessions for this project from `~/dev/past-performance`, not here.

## claude-sync lives outside this tree

As of 2026-08-05, **claude-sync is no longer under `~/Documents/dev/`** —
relocated in full to `~/dev/claude-sync` via `ditto` (2,717 entries).
Cleanest of this batch: clean tree modulo one uncommitted `CLAUDE.md` doc
change (stashed/restored), no nested worktrees, all 3 LaunchAgents
(`com.ogreen.claude-sync`, `.healthcheck`, `.menubar`) repointed and reloaded
without incident. `.venv/bin/python3` is a relative symlink, same as
network-scanner, so no shebang fallout. Confirmed live via its own startup
log (watching `~/.claude/projects`, HTTP bound on :8866). Start sessions for
this project from `~/dev/claude-sync`, not here.

## scribe lives outside this tree

As of 2026-08-05, **scribe is no longer under `~/Documents/dev/`** - its own
separate repo (github.com/ogreen111/scribe), relocated in full to
`~/dev/scribe` via `ditto` (44,333 entries). Already using both the
`.git -> .git.nosync` and `.venv -> .venv.nosync` conventions before this
move. A local branch `slice-08-observability` (one commit, never pushed) had
to be pushed to origin first to satisfy the preflight check. Migrating an
already-`.git.nosync`-converted repo surfaced two real `migrate-project.sh`
bugs, fixed in that script's own commit: `git worktree list` resolves the
main worktree's path through the `.git.nosync` symlink rather than reporting
the repo root, and `diff -rq`'s directory-loop detection false-positives on
any directory reachable two ways within the same parent - hit here on
`.git.nosync`, `.venv.nosync`, and the Swift Package Manager
`.build/debug -> arm64-.../debug` convenience symlinks. The venv was rebuilt
with the project's real production extras (`pip install -e
".[mlx,diarization,dev]"`, matching `deploy/install.sh`'s step 2, not the
minimal dev recipe) - `ssi-scribe doctor` confirmed ffmpeg, MLX ASR,
diarization, OCR, and the shared LLM all healthy afterward, with cached
models (`~/.cache/huggingface`, unaffected by the move) reused without
re-downloading. LaunchAgent confirmed live over HTTPS (`GET /` → 200 on
:8736, real LAN client traffic visible in logs immediately). Start sessions
for this project from `~/dev/scribe`, not here.

## cyber-artifact-gen, daily-summary, cyber-brain, outlook-followup, kml live outside this tree

As of 2026-08-05, these five are no longer under `~/Documents/dev/` — moved
to `~/dev/` in a batch. Much smoother than prior batches: none have
LaunchAgents, none had nested Claude Code worktrees, and only
`cyber-artifact-gen` had uncommitted work (4 modified SSi brand-bundle
files, stashed/restored cleanly). `cyber-brain` has no `.venv` yet on this
machine (never synced here), so `uv run` will build one fresh with no
stale-path risk. `outlook-followup` and `kml` have **no `.git` of their
own** — both are listed in this repo's own `.gitignore` with zero tracked
files (`git ls-files` confirms), so they moved as plain files with no
push-safety check possible (the script's documented behavior for non-git
projects) rather than as independent repos.

Two remaining projects in the registry, **`PRTG Import`** and
**`Pocket Probe`**, have spaces in their directory names and can't be
migrated via `migrate-project.sh` as-is — its own project-name safety regex
(`^[A-Za-z0-9._-]+$`) rejects them outright. Rename (or extend the script)
before attempting either.

**`account-store`** was deliberately deferred past every routine batch
above because of its shared-dependency blast radius. While deferred, a
bridge symlink (`~/dev/account-store -> ~/Documents/dev/account-store`,
added to `.gitignore` **without** a trailing slash - the trailing-slash
form doesn't match a symlink, same gotcha as `.venv*` below) let
relative-path consumers like `project-monitor`/`project-creation` resolve
it correctly from their new `~/dev/` locations in the meantime. See
"account-store migrated, all 8 dependents re-pointed" below for the full
resolution, including why that symlink turned out not to be a durable fix
on its own.

## ssi-design-system, claude-memory-compiler, sanguine, project-monitor live outside this tree

As of 2026-08-05, these four are no longer under `~/Documents/dev/` — moved
to `~/dev/` in a batch. `ssi-design-system` and `sanguine` both had a
pre-existing nested Claude Code worktree needing `git worktree remove`
first (same safe profile as prior batches); `ssi-design-system` also had an
untracked brand-asset folder (`2022 Spectrum Logos/`, legitimate content,
stashed/restored). `sanguine` separately turned up three *orphaned*
`.claude/worktrees/*` directories whose `.git` files point at
**dev-portfolio's own** (already-deleted) worktree admin data, not
sanguine's - inert leftover clutter from some earlier session, carried
along by `ditto` as-is; not a sanguine or migration problem, left alone.

All three with a `.venv` had the same stale-shebang fallout as every prior
batch - `uv sync` alone often reports success ("Checked N packages")
without actually regenerating console scripts if it thinks the lockfile is
already satisfied, so a clean `rm -rf .venv .venv.nosync && uv sync` (per
each project's own README) was needed, not just a plain re-sync.
`claude-memory-compiler` was the one exception: its `bin/uvr.sh` wrapper
deliberately keeps its uv-managed venv entirely outside the synced tree
(`UV_PROJECT_ENVIRONMENT=~/.local/share/uv-venvs/claude-memory-compiler`),
so there was no in-project venv to rebuild at all - just `PROJECT_DIR` in
that wrapper script itself needed the path fix (missed by the script's
`EXTRA_FIXUP_FILES` pass because the file was untracked and got stashed
away *before* the copy ran, then restored after - had to be re-applied by
hand). More importantly, **`~/.claude/settings.json`'s own SessionStart /
PreCompact / SessionEnd hook commands hardcoded the old absolute path** to
`bin/uvr.sh` - entirely outside any project tree the migration script could
see, so it would have silently broken the memory-compiler's automatic
flush hooks on every future session event. Fixed by hand and verified
(`hooks/session-start.py` runs correctly from the new path).

## ethernet-link-analyzer, virtual-devices, trim-backup, sops, stream-deck, fulcrum-replacement live outside this tree

As of 2026-08-05, these six are no longer under `~/Documents/dev/` — moved
to `~/dev/` in a batch. `sops`, `stream-deck`, and `fulcrum-replacement`
have no `.git` of their own (gitignored, untracked plain directories, same
as `outlook-followup`/`kml` earlier). `ethernet-link-analyzer` had a
nested Claude Code worktree (`.claude/worktrees/vibrant-rubin-571ac8`,
branch `claude/vibrant-rubin-571ac8`) with **real uncommitted work** (4
modified files, an in-progress LLDP/parser fix) - unlike every prior
nested-worktree case, which were all clean/detached-HEAD. Handled by
stashing inside the worktree, removing it, migrating, then recreating the
worktree at the new location on the same branch (`git worktree add`) and
popping the stash back - fully verified identical afterward. `virtual-devices`
and `ethernet-link-analyzer` both had stale-shebang venvs, rebuilt per
each project's own documented recipe (the latter has a real macOS +
Python 3.14 hidden-`.pth` gotcha independent of iCloud - see its own
README - requiring `chflags -R nohidden .venv` after install).

**Also discovered this round: `deploy` is *not* an independent project
either** - like `siem-forwarder`, it has no `.git` of its own and is
**not** gitignored: its 1 tracked file (`com.ssi.portfolio.plist` - this
portfolio's own LaunchAgent, doesn't belong anywhere else) lives directly
in dev-portfolio's own history. Don't run `migrate-project.sh` on it -
`git ls-files <dir>` first on any project without its own `.git` before
attempting to move it. (`project-creation` was in this same category -
see below for how it was resolved.)

## project-creation extracted into its own repo

As of 2026-08-05, **`project-creation` is no longer tracked inside
dev-portfolio at all** - like `siem-forwarder` and `deploy` above, it had
no `.git` of its own but (unlike `sops`/`stream-deck`/`fulcrum-replacement`)
27 files were tracked directly in this repo's own history (5 commits of
real work: scaffold, Graph app-only auth, SharePoint resolver). Rather
than just moving it as plain files and losing that history, it was
properly extracted:

- `git subtree split --prefix=project-creation -b project-creation-extract`
  rewrote those 5 commits with `project-creation/` stripped from every
  path, producing a standalone-ready branch.
- A new private GitHub repo was created
  (`github.com/ogreen111/project-creation`, matching every other real
  project's `github.com/ogreen111/<name>` pattern) and the extracted
  branch pushed to it as `main`.
- `project-creation/` was `git rm -r --cached` from dev-portfolio (both
  local clones - see the `~/Documents/dev` vs `~/dev` note above) and
  added to `.gitignore`, same as every migrated project. The untracked
  `.plans/` planning docs (never tracked here, per this repo's own
  gitignore convention) were copied over by hand since `subtree split`
  only carries tracked history.
- **Caution if you ever do this again:** don't run `git remote
  add`/`remote remove` from inside a subdirectory that has no `.git` of
  its own - it silently falls through to the *parent* repo's git context.
  Hit this live: a `cd project-creation && git remote add origin
  <new-repo>` actually repointed `~/dev`'s own dev-portfolio remote before
  it was caught and fixed. Always clone the extracted branch into a
  **separate, unrelated path** (e.g. the scratchpad) first, configure its
  remote there, and only move it into `~/dev/<name>` after the source has
  been fully removed from dev-portfolio's tracking.
- `pyproject.toml` has two relative-path dependencies -
  `account-store = { path = "../account-store", ... }` and `rfp-automation
  = { path = "../rfp-automation", ... }` - both resolve correctly from
  `~/dev/project-creation` (the former via the bridge symlink documented
  above, the latter since `rfp-automation` already lives at
  `~/dev/rfp-automation` for real). `uv sync --extra dev` (Python 3.12,
  auto-fetched by uv) didn't create the `.venv` symlink on its own again
  (same as `sanguine` earlier) - created by hand. Verified: all three
  modules import, 50 tests collect.

## siem-forwarder extracted into its own repo

As of 2026-08-05, **`siem-forwarder` is no longer tracked inside
dev-portfolio at all** - same situation and same fix as `project-creation`
above: 20 files and 5 real commits (Niagara bind-point resolution, alarm
forwarding, two bug fixes, an SDD sync) were tracked directly in this
repo's history with no independent `.git`. Extracted via `git subtree
split --prefix=siem-forwarder`, pushed to a new private repo
(`github.com/ogreen111/siem-forwarder`), removed from dev-portfolio's
tracking and added to `.gitignore`. The untracked
`siemForwarder-SDD-AddendumA.docx` was copied over by hand, same reason as
`project-creation`'s `.plans/`. This one had no nested worktree and no
`.plans/`, so it was simpler - but the extracted branch was still cloned
into the scratchpad first, not directly into `~/dev/siem-forwarder`,
per the gotcha documented above.

Unlike every other migrated project, **this one can't be build-verified
here**: `build.gradle` requires Tridium's Niagara Gradle plugin, resolved
from a licensed Niagara 4.10+ install via the `niagara_home` env var
(local dev bundle, not Maven Central) - not present in this environment.
Verification stopped at file-level (`diff -rq --no-dereference` clean,
correct 5-commit history, correct paths) rather than a working build.

**Also investigated and resolved differently: `deploy` is not a
project at all.** Its one tracked file, `com.ssi.portfolio.plist`, is
dev-portfolio's *own* LaunchAgent config for its portfolio index dashboard
(`~/dev/portfolio_server.py`, port 8737 - see Port Map). It correctly
lives inside dev-portfolio permanently, like `scripts/` - there's nothing
to extract or migrate. Confirmed the tracked copy has drifted slightly
from what's actually installed at `~/Library/LaunchAgents/` (a stale
comment block about TLS handling) - worth a `cp` sync on next touch, but
that's routine drift, not a migration blocker.

## pocket-probe and prtg-import live outside this tree (renamed, spaces removed)

As of 2026-08-05, the two projects with spaces in their directory names
(previously listed as `PRTG Import` and `Pocket Probe` in the registry
table above, now renamed there too) are now
`~/dev/pocket-probe` and `~/dev/prtg-import` - `migrate-project.sh`'s own
project-name safety regex (`^[A-Za-z0-9._-]+$`) rejects spaces outright, so
both were renamed to kebab-case (matching this portfolio's convention)
before migrating. Neither rename needed a GitHub rename to match: PRTG
Import's remote was already `PRTG-Import` (hyphenated); Pocket Probe never
had one (see below).

**`Pocket Probe`'s git history was corrupted** - `git status` failed with
"fatal: bad object HEAD", `git fsck` found the ref pointing at a
nonexistent commit and dozens of missing blobs, and no remote had ever
been configured. The reflog showed only 2 commits ever existed ("Initial
commit" and "Add README and MIT LICENSE", both from May). Investigated a
Time Machine recovery path (`tmutil listbackups` showed history back to
June 3, which postdates both commits) but the backup destination wasn't
actually mounted/browsable in this environment. **Critically, the
*working-tree files* were completely unaffected by the git corruption** -
`.gitattributes`, `LICENSE`, `README.md`, and the full KiCad
hardware/STM32 firmware source (1013 files) were all intact; only the
version-history metadata was broken, and only 2 small early commits'
worth of it. Resolved by backing up the broken `.git` (see
`pocket-probe/`'s own git reflog - it's a fresh history now, so the old
one isn't visible there) and reinitializing fresh from the intact working
tree as a single commit. Given a real backup, created
`github.com/ogreen111/pocket-probe` (private) this time and pushed.

**`PRTG Import` had a real, substantial merge conflict** - local `main`
and `origin/main` had diverged since May: origin had a large refactor
(site-based grouping, dry-run mode, hardened API, ~965 lines across all 3
tracked files) that local had never pulled, while local had a smaller
recent commit (a new `PRTGreport.ps1` uptime-report script, purely
additive - no actual file overlap) plus 299 lines of *stashed, never
committed* work based on the old pre-refactor files. The commit-level
merge (refactor + new report script) applied cleanly with zero real
conflicts - `git merge-tree` initially looked like it conflicted, but
that was a misread of its normal informational merge-result diff, not an
actual `CONFLICT` marker. The *stashed* uncommitted work was the real
conflict (7 blocks in `PRTGimport.ps1`, 6 in `README.md`, 1 in the config
example) - it added a `-ValidateOnly` parameter that overlapped in intent
with the refactor's independently-added `-DryRun`, among other
CSV-field-flexibility and dedup logic. Rather than guess at reconciling
PowerShell logic across two independently-evolved feature sets, dropped
the stash and kept only the clean merge - the `-ValidateOnly` work (and a
"Tracker Sync" README section documenting `sync-tracker.py`/`gap-report.py`,
which still exist as untracked files at the new location) can be
reconciled later by hand if still wanted. Also has an old orphaned nested
clone at `prtg-import/previous/` (same repo's March root commit, its own
unmerged uncommitted edits) - carried along as-is per instruction, moved
via `ditto` (not `mv` - hit the exact same iCloud cross-boundary deadlock
this whole script exists to avoid, moving it to the scratchpad and back).

## account-store migrated, all 8 dependents re-pointed

As of 2026-08-05, **`account-store` is no longer under
`~/Documents/dev/`** - relocated in full to `~/dev/account-store` via
`ditto`, the last portfolio project to move. A pre-existing nested
Claude Code worktree (`.claude/worktrees/intelligent-lalande-d5e1cd`,
detached HEAD, clean, fully pushed) was removed first, same profile as
every other one this session. The bridge symlink documented above
(`~/dev/account-store -> ~/Documents/dev/account-store`) had to be
deleted *before* running `migrate-project.sh` - the script's own
`[ -e "$NEW" ] && FATAL` check would otherwise refuse to create the real
directory at a path the symlink already occupied.

Every dependent needed re-pointing, confirmed by surveying each one's
*actual* reference mechanism rather than assuming - they turned out to be
five genuinely different patterns, not two:

1. **Hardcoded absolute path in `pyproject.toml`** (`cert-manager`) - edit
   the one line, rebuild the venv.
2. **`uv`/setuptools editable install** (`email-processor`,
   `past-performance`) - the installed `__editable__..._finder.py` bakes
   a `MAPPING` dict with the *absolute* resolved path at install time (see
   point 5 below for why this matters), so editing `pyproject.toml` alone
   does nothing; needs an actual reinstall
   (`uv pip install --python .venv/bin/python -e ~/dev/account-store`).
3. **Direct symlink into `site-packages`** (`project-tracking`, per its
   own `AGENTS.md` recipe - a Python-3.14-specific workaround for
   setuptools' editable shim dropping hidden `.pth` files) - just
   recreate the symlink at the new target.
4. **Bare `PYTHONPATH` env var**, no pip install at all (`rfp-automation`)
   - baked into 8 separate files that needed fixing in lockstep: the
   installed `~/Library/LaunchAgents/com.rfpautomation.{dashboard,watcher}.plist`
   themselves (`EnvironmentVariables.PYTHONPATH`), 5 tracked-but-gitignored
   `output/live_monitor/*.plist` mirror copies, and the actual source of
   truth, `scripts/launchd_dashboard_wrapper.sh`. That first pass still
   missed a real one - see the correction below. Editing the installed
   plists needed a full `bootout` + `bootstrap` (not `kickstart -k` -
   changed `EnvironmentVariables` needs the plist definition itself
   reloaded, not just the process restarted).
5. **`tool.uv.sources` relative path** (`project-monitor`, `project-creation`
   - `{ path = "../account-store", editable = true }`). This is the
   important one to understand: a relative source declaration does **not**
   provide ongoing resilience to account-store moving - `uv sync` still
   resolves it to an absolute path *at install time* and bakes that into
   the installed finder script, identically to pattern 2 above. The
   bridge symlink documented earlier only worked because it existed at
   the moment these were installed; once account-store moved for real and
   the symlink was removed, both needed the exact same
   `rm -rf .venv .venv.nosync && uv sync` treatment as every absolute-path
   editable install elsewhere in this portfolio - no exemption for having
   used the relative form.

All 5 live services (`cert-manager` backend, `email-processor` webserver,
`past-performance`, `rfp-automation` dashboard + watcher, `project-tracking`)
were bounced and confirmed genuinely healthy afterward, not just
"restarted": `cert-manager` `GET /api/health` → `200`; `email-processor` →
`401` (auth-gated, expected); `past-performance` → `302` (login redirect,
expected); `project-tracking` → `200` over HTTPS; `rfp-automation`
dashboard log showed the *old* process's `ModuleNotFoundError` crashes
ending precisely at the restart timestamp, with clean `200`/`303`
responses immediately after; `rfp-automation` watcher's own log showed
zero `ModuleNotFoundError` occurrences post-restart, just normal
"Using cached access token" activity.

**The first "final grep came back clean" claim here was wrong** - it used
`2>/dev/null`, which silently swallowed whatever made the wide `~/dev/`
recursive grep miss real matches it found fine when scoped to a single
project directory (never fully diagnosed; suspected resource limits on
such a large recursive tree). A Codex pre-commit review caught it live
and it's worth remembering generally: don't trust an error-suppressed
grep's silence as proof of a clean sweep, especially over a big tree.
Rerunning without suppression turned up a genuinely missed **8th
consumer, `digital-twin`** (`twin/auth.py`'s docstring, `CLAUDE.md`'s
`ln -s` recipe, a `CHANGELOG.md` mention) - not in the original 7-project
survey at all, and a real functional break: `twin/auth.py` genuinely *is*
imported (`twin/web.py` does `from . import auth` and calls
`auth.gate(request)` on every request; `twin/routes/admin.py` and
`twin/routes/session.py` import it too - a first check here that searched
for `import twin.auth`/`from twin.auth import` missed this relative-import
style entirely). Its `.venv/lib/python3.14/site-packages/account_store`
symlink existed but was stale (pointing at the deleted
`Documents/dev/account-store` - a second check here missed it too, using
`find -maxdepth 4` on a path that's actually 5 levels deep). Fixed both
and verified `twin.auth` now imports cleanly. `twin.web`'s *full* import
chain also had an unrelated, pre-existing gap at the time (`niagara_config`
not installed in this venv at all) - since resolved (see "digital-twin's
BACnet and DB issues fixed" below): `niagara_config` is now installed,
`twin.web` imports cleanly, and `com.ssi.digital-twin` is loaded and
serving the HMI. Also found and fixed real broken command examples
in `rfp-automation`'s `README.md`/`CLAUDE.md`/`AGENTS.md` and a
**functional break**: its
`.claude/launch.json` (the actual dev-server preview config used by this
harness's own `preview_start`, not just docs) had the stale `PYTHONPATH`
baked in too - fixed and committed in that repo along with the doc
fixes. `project-tracking` had four more stale doc references beyond the
two caught initially (`AGENTS.md`, `CLAUDE.md`, `README.md`, plus the
`webapp/auth.py` docstring). All three affected repos (`rfp-automation`,
`project-tracking`, `digital-twin`) got their own commits, separate from
this one. A properly-verified sweep (no `2>/dev/null`, scoped file-by-file
rather than trusting one wide recursive call) now comes back clean.

## digital-twin's BACnet and DB issues fixed

As of 2026-08-06, `com.ssi.digital-twin` is loaded and its `niagara_config`
gap (noted above) is resolved - `.venv/bin/python -c "import niagara_config"`
and `from twin import web` both succeed, and the LaunchAgent serves the HMI
on :8080. Two separate issues reported as "database corruption" and
"BACnet issues" were investigated and resolved:

- **DB "corruption"**: `twin/fdd/event_store.py`'s `EventStore` already
  self-heals via `_rebuild_if_corrupt()` (a `PRAGMA integrity_check` on
  init, discarding the DB + WAL/SHM/journal sidecars if it fails). Verified
  the live `.state.nosync/twin_events.sqlite` passes integrity check
  cleanly (145 rows) - no action needed, the existing safeguard already
  did its job.
- **BACnet init failing under launchd, but working when run interactively**:
  root cause was `~/Library/LaunchAgents/com.ssi.digital-twin.plist`'s
  `EnvironmentVariables.PATH` (`/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin`)
  missing `/sbin`, where `ifconfig` lives. `twin/controllers.py`'s
  `_autodetect_macos_iface()` shells out to `ifconfig` to work around a
  known BAC0-on-macOS netmask-detection bug; under the restricted launchd
  PATH the `ifconfig` call silently failed, `_autodetect_macos_iface()`
  returned `None`, and BAC0's own broken autodetect then threw
  `NetmaskValueError: 'None' is not a valid netmask`. Fixed by adding
  `/usr/sbin:/sbin` to the plist's `PATH` and reloading with `bootout` +
  `bootstrap` (`kickstart -k` alone doesn't pick up changed
  `EnvironmentVariables`). Confirmed via the error log: BACnet now
  auto-detects the LAN interface and comes up on port 47808. No tracked
  plist template exists in the digital-twin repo for this LaunchAgent -
  the installed copy at `~/Library/LaunchAgents/com.ssi.digital-twin.plist`
  is the only source of truth.

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
  `.venv/bin/...` commands (e.g. the Port Map below) keep working.
- Migrating an existing project: `rm -rf .venv .venv.nosync && uv sync && ln -s .venv.nosync .venv`
  (only when nothing is running from the venv). Removing only the `.venv`
  symlink and leaving `.venv.nosync` in place lets `uv sync` reuse the
  moved environment as-is instead of rebuilding it — console-script
  shebangs baked in at the old path stay stale. Ensure `.gitignore` uses
  `.venv*`, not `.venv/` (a symlink isn't matched by the trailing-slash form).
- Migrated so far: project-monitor, ssi-design-system, niagara-llm, sanguine,
  digital-twin/frcs-digital-twin, rfp-automation, project-tracking,
  email-processor, scribe (`.venv` is a symlink to `.venv.nosync`).
- Don't write per-file workarounds (runtime import shims, chflags hooks) —
  they lose the race or rot.

---

## `.git` lives in `.git.nosync` (same iCloud workaround)

The repo's own `.git` directory hit the identical failure mode as venvs: iCloud
duplicated files inside it (refs, `COMMIT_EDITMSG`, etc.) when it didn't like
concurrent access, producing broken-named refs (`refs/heads/main 2`, `main 3`)
and `git branch -a` warnings. Fixed 2026-08-03 the same way as venvs:

- The real git directory was moved to `~/Documents/dev/.git.nosync`; `.git` at
  the repo root is now a symlink to it (`.git -> .git.nosync`).
- This is safe for the repo's many linked worktrees: each linked worktree's own
  `.git` file hardcodes an absolute path like
  `gitdir: /Users/ogreen/Documents/dev/.git/worktrees/<name>`, which still
  resolves correctly through the `.git` symlink — no worktree files needed
  updating.
- `.gitignore` has a `.git.nosync` entry so the real directory doesn't show up
  as a giant untracked folder in `git status` (git only auto-hides the literal
  `.git` path, not a renamed one).
- Verified fixed via the same test as venvs: `chflags nohidden` on a file
  inside `.git.nosync` did not get reverted after a couple seconds (an
  actively-synced item reverts within ~0.5s).
- If this repo is ever re-cloned or a new worktree tooling flow bypasses the
  symlink, redo the same move: `mv .git .git.nosync && ln -s .git.nosync .git`
  (only when no git operation is in progress and no lockfiles exist).

---

## Port Map

Reserved ports for the dev portfolio. Each app binds its assigned port on startup; do not double-book.

| Port | Project | Service | Start command |
|---|---|---|---|
| 8000 | network-scanner | FastAPI backend | `cd ~/dev/network-scanner && .venv/bin/python -m uvicorn scanner.app:app --host 0.0.0.0 --port 8000` (not `.venv/bin/uvicorn` directly - that console script has a stale shebang) |
| 8002 | cert-manager | FastAPI backend | `cd ~/dev/cert-manager/backend && .venv/bin/uvicorn app.main:app --port 8002` |
| 8008 | rfp-automation | dashboard (stdlib HTTP) | `cd ~/dev/rfp-automation && .venv/bin/rfp-auto dashboard` (reads `RFP_DASHBOARD_PORT` from `.env`) |
| 8080 | digital-twin | Flask HMI | `cd ~/dev/digital-twin/frcs-digital-twin && WEB_HMI_PORT=8080 .venv/bin/python -m twin.cli run` |
| 8081 | digital-twin | Niagara oBIX server (emulator) | `cd ~/dev/digital-twin/frcs-digital-twin && TWIN_ENABLE_NIAGARA=1 .venv/bin/python -m twin.cli run` (gated by `TWIN_ENABLE_NIAGARA=1`) |
| 8082 | digital-twin | Niagara REST/BQL endpoint (emulator) | same process as oBIX above (`NIAGARA_BQL_PORT`) |
| 8736 | scribe | uvicorn terminates TLS directly (mkcert cert), no reverse proxy | LaunchAgent `com.ssi.scribe` (https://host:8736) |
| 8737 | dev-portfolio | Plain HTTP (`ThreadingHTTPServer`), no TLS — `PORTFOLIO_SSL_CERTFILE`/`KEYFILE` are set but `portfolio_server.py` never reads them (details/caveats: [PORTS.md](PORTS.md)) | `launchctl kickstart -k gui/$(id -u)/com.ssi.portfolio` (binds 0.0.0.0:8737) |
| 8765 | email-processor | FastAPI + uvicorn | `cd ~/dev/email-processor && make serve` (applies the `chflags nohidden` .pth workaround; a bare `uv run` re-hides the file on its next sync) |
| 8767 | past-performance | FastAPI + uvicorn | `cd ~/dev/past-performance && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8767` |
| 443 | project-tracking | uvicorn terminates TLS directly (mkcert cert), no reverse proxy — cutover complete 2026-07-06, the old plaintext `:8768` endpoint is retired (see `project-tracking/docs/DEPLOYMENT.md`) | LaunchAgent `com.ssi.project-tracking` (https://localhost/ on this Mac, or https://og-work-mac-studio-2.local/ over the LAN — note the `-2`: this machine's `LocalHostName` is `OG-Work-Mac-Studio-2`, so the un-suffixed `og-work-mac-studio.local` resolves to nothing, and the old `10.10.10.92` is no longer one of its addresses. Both names are in the mkcert SANs; only the addresses went stale) |
| 8769 | project-monitor | FastAPI + uvicorn | `cd ~/dev/project-monitor && PM_PORT=8769 .venv/bin/project-monitor run` |
| 8770 | niagara-llm | FastAPI + dashboard | `cd ~/dev/niagara-llm && uv run niagara-llm run` |
| 8771 | sanguine | FastAPI + dashboard | `cd ~/dev/sanguine && uv run sanguine run` (reads `SANGUINE_PORT`) |
| 8772 | cyber-brain | FastAPI + dashboard | `cd ~/dev/cyber-brain && uv run cyber-brain run` (reads `CB_HOST`/`CB_PORT`; binds 127.0.0.1 by default) |
| 8773 | project-creation | FastAPI (default `PROJECT_CREATION_PORT`) | reserved — `project_creation.app:create_app()` exists but the CLI (`project-creation`) is still a stub with no `run`/uvicorn wiring yet |
| 8774 | fulcrum-replacement | FastAPI + offline-first mobile app (planned) | reserved only — `fulcrum-replacement/` has no `pyproject.toml` or app code yet, just `DESIGN.md`/`DESIGN.docx`; no start command exists until it's built |
| 5173 | cert-manager | Vite frontend (proxies `/api` → 8002) | `cd ~/dev/cert-manager/frontend && npm run dev` |

**Notes:**

- past-performance, project-tracking, and email-processor all default to 8765 in their own READMEs; the portfolio-wide assignment moves them apart so they can run simultaneously.
- cert-manager's Vite proxy target in `frontend/vite.config.ts` must match the backend port (currently `8002`).
- **Avoid port 8766** — silently reserved at the OS level on this machine (visible via `netstat` as LISTEN on `127.0.0.1:8766` but with no `lsof`-visible owner).
- The `claude-sync` daemon binds `127.0.0.1:8866` (not a portfolio app server, but reserves the port).

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
