# siemForwarder — non-interfering SIEM event forwarder for JACE / Niagara 4

A Niagara station service that forwards security-relevant events (point
value/status changes, alarms, audit records) from a JACE to a SIEM over
syslog/TLS — **without adding any load to the RS-485 field bus or the control
engine.**

This is a **skeleton**: the structure, threading model, and the three safety
patterns are complete and correct, and the framework call sites have been
rewritten against the real Niagara API surface (verified on 4.15.1 class
files — see SDD §11.1/Appendix B). A small number of genuine bind points that
vary by Niagara build are marked inline (`BIND POINT:` / commented) for you to
bind against your target `niagara_home`. It will need the slot-o-matic run and
the real alarm/audit listener types wired before it compiles clean.

## The three patterns you asked for

### 1. Ride-along subscription check (`RideAlongSubscriber`)
The trap: calling `Subscriber.subscribe(point)` forces a proxy point into the
driver's poll set, adding real traffic to the RS-485 trunk and perturbing MS/TP
token timing / Modbus poll cycles. So a naive "monitor" is *not* passive.

The rule this module enforces: **only attach to points that are already
subscribed by someone else** (graphics, histories, control logic). Niagara
ref-counts subscriptions, so joining an existing one adds **zero** polls. A
cheap in-memory rescan (every 10s, no wire traffic) picks up newly-active points
and releases ones that went idle — we never keep a point polled on our own
account. Alarms and audit records bypass this gate entirely because they're
station-internal and never touch the field bus.

### 2. Bounded queue (`BoundedEventQueue` + `ForwardWorker`)
- Event handlers do nothing but `offer()` and return — microseconds, no I/O.
- A single **below-normal priority** worker thread owns the socket. The engine
  and driver threads always out-prioritize it.
- The queue is fixed-capacity and **drop-oldest**: under pressure, SIEM data is
  shed, never engine time, and the heap can't grow unbounded from a stalled
  collector. Drops are counted and surfaced back to the SIEM as an explicit
  `gap` event so you never silently lose visibility.
- Reconnect with exponential backoff (1s → 60s). A SIEM outage never blocks or
  wedges the station.

### 3. Self-throttle (`SelfThrottleMonitor`)
Watches engine-hog % and free-heap %. State machine:
`NORMAL → THROTTLING → SUSPENDED`, auto-recovering.
- **THROTTLING** — only warning-and-above events pass; deadband widens.
- **SUSPENDED** — all data events dropped; a 30s **heartbeat** still goes out so
  the SIEM can distinguish "feed intentionally paused" from "collector died."
- A slow (5 min) **liveness heartbeat** also runs in NORMAL/THROTTLING, so a
  quiet station is distinguishable from a dead module.
- The monitor tick doubles as a **write-stall watchdog**: if a socket write to
  a half-open SIEM blocks longer than 30s (Java sockets have no write timeout),
  it closes the socket so the worker reconnects with backoff.
- **Fail-open**: monitoring pauses, control never does. Monitoring can't take
  down the thing it's monitoring.

## Layout
```
siemForwarder/
├── build.gradle                 root build (Tridium niagara-module plugin)
├── settings.gradle
├── siemForwarder-rt/
│   ├── build.gradle             module build + signing hooks
│   ├── module-include.xml       module profile + type defs
│   ├── module.palette           drag-in palette for Workbench
│   └── src/
│       ├── META-INF/module-permissions.xml   SecurityManager socket grant
│       └── com/acme/siem/
│           ├── BSiemForwarderService.java     config + lifecycle + wiring
│           ├── RideAlongSubscriber.java       pattern #1
│           ├── BoundedEventQueue.java         pattern #2 (queue)
│           ├── ForwardWorker.java             pattern #2 (socket owner)
│           ├── SelfThrottleMonitor.java       pattern #3
│           ├── SiemEvent.java                 immutable event POJO
│           └── SyslogFormatter.java           RFC 5424 output
├── tests/
│   ├── run-tests.sh              standalone runner (plain javac/java, no Niagara)
│   └── src/com/acme/siem/        unit tests for the pure-Java classes
```

## Unit tests (no Niagara toolchain required)

`BoundedEventQueue` and `SiemEvent` are deliberately dependency-free, so their
tests run outside the Gradle build (which needs the Tridium plugins and a
Niagara dev bundle to even configure). The runner compiles the two production
classes plus the tests directly with `javac` and runs a tiny zero-dependency
harness — any JDK 8+ works:

```
./tests/run-tests.sh
```

The script finds a JDK via `$JAVA_HOME`, the PATH, `/usr/libexec/java_home`,
or a Homebrew `openjdk` install, compiles into `tests/build/` (regenerated
each run), and exits non-zero on any failure. The tests live in
`com.acme.siem` because both classes are package-private.

Coverage (SDD §test-plan T1/T2 plus contract checks):
- **T1 — drop-oldest under overflow**: enqueue > capacity with no consumer;
  newest events retained in FIFO order, oldest shed, `dropped()` exact, and
  the constructor's capacity floor of 16.
- **T2 — `offer()` never blocks**: 100k saturated offers with no consumer,
  every call must return in under 1 ms (retried to ride out GC noise).
- `poll()` timeout/null behavior, immediate return when non-empty, and
  wake-up of a blocked poller on `offer()`.
- `countExternalDrop()` counter semantics.
- `SiemEvent` factory methods: kind, fixed severities (audit 5, heartbeat 6,
  drop-report 4), fixed `siemForwarder` source, null-source → `"-"` and
  null-message → `""` defaults, drop count surfaced in the gap message.

## Build & install
1. Install Niagara 4.10+ dev bundle; set `niagara_home`.
2. `./gradlew :siemForwarder-rt:jar` (or `moduleTestJar` during dev).
3. **Code-sign** the JAR. For RMF/DoD, use a cert chaining to an approved CA —
   do not lower the signing policy.
4. Copy `siemForwarder-rt.jar` to `!modules`, restart the station.
5. In Workbench, drag `SiemForwarderService` from the palette into
   `Station/Config/Services`.
6. Configure `siemHost`, `siemPort`, `useTls`, and `networkOrd` (the driver
   subtree to watch). Confirm the TLS trust store on the platform trusts your
   SIEM collector.

## Before you build — framework-version bind points
- Run the **slot-o-matic** to regenerate the auto-generated block in
  `BSiemForwarderService` (the hand-written version — including the
  `rideAlongRescan` / `throttleTick` action slots the clock tickets dispatch
  through — is there so the skeleton reads cleanly).
- Replace the engine-hog approximation with the authoritative reading from your
  build's `EngineWatchdogService`/`SysManager`.
- Wire the alarm and audit listeners in `hookAlarmAndAudit()` to the concrete
  `BAlarmService` / `BAuditHistoryService` types on your target.
- TLS trust is currently anchored in the **JVM-default** trust store
  (`SSLSocketFactory.getDefault()`, with hostname verification enabled). To
  anchor it in the **Niagara platform certificate store** instead, build the
  `SSLSocketFactory` from the platform certificate-manager API on your target
  build (marked `BIND POINT:` in `ForwardWorker.connect()`).
- Update the `SocketPermission` in `module-permissions.xml` to match your
  configured `siemHost`/`siemPort` (the shipped grant is the default host).

## Monitoring-coverage caveat (worth knowing before the ISSO asks)
Ride-along means point coverage is **opportunistic**: only points some other
component keeps subscribed (graphics, histories, control logic) are ever
visible to the SIEM, and the monitored set changes as Px views open/close. A
point with no external interest is never forwarded — by design, because
subscribing it ourselves would add RS-485 traffic. If a point must be
guaranteed in the SIEM feed, give it a history extension (or other standing
subscriber); that also makes coverage deterministic for accreditation
evidence. Alarms and audit records are unaffected (forwarded unconditionally).

## RMF / accreditation notes
Custom code on the JACE enters your accreditation boundary and will be scrutinized
under CM and SA controls. This module is designed to make the **non-interference
argument** easy to evidence: baseline engine hog, MS/TP token loop time, and
Modbus poll cycle before install, then re-measure with the module running under
load — the delta is your AU/SA evidence. Pair this (point + alarm data) with
Niagara's native remote syslog (4.10+, for platform/audit logs) to cover AU
controls with the smallest custom-code surface.
