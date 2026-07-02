package com.acme.siem;

import javax.baja.log.Log;
import javax.baja.sys.*;

/**
 * SelfThrottleMonitor
 * -------------------
 * Watches the JACE's own health and pulls back the SIEM feed BEFORE it can
 * become a load problem. Fail-open by design: if the station is stressed, the
 * monitoring is what pauses — control never does.
 *
 * Two signals, both cheap to read:
 *   - engineHogPct : how much of the engine cycle is being consumed. Rising hog
 *                    means the control engine is busy; we back off.
 *   - freeHeapPct  : JVM headroom. Low heap means we stop generating garbage
 *                    (event objects, formatted strings) and let GC recover.
 *
 * State machine:  NORMAL --(pressure)--> THROTTLING --(worse)--> SUSPENDED
 *                    ^-------------(recovered)-----------------------|
 *
 *   NORMAL     - forward everything (still bounded + deadbanded upstream).
 *   THROTTLING - raise effective min-interval; only higher-severity events pass.
 *   SUSPENDED  - drop all data events; emit only a periodic heartbeat so the SIEM
 *                can tell "feed intentionally paused" from "collector died."
 *
 * Heartbeats: a fast (30 s) heartbeat while SUSPENDED, plus a slow (5 min)
 * liveness heartbeat in every other state — so on a quiet station the SIEM can
 * still distinguish "nothing happening" from "module/station dead."
 *
 * Runs on the app clock (no dedicated thread). Also drives refreshTelemetry()
 * and the worker's write-stall watchdog.
 */
final class SelfThrottleMonitor
{
  private static final Log log = Log.getLog("siemForwarder");

  // Thresholds (percent). Tune per platform during baseline testing.
  private static final double HOG_THROTTLE = 15.0;   // engine hog % to start throttling
  private static final double HOG_SUSPEND  = 30.0;   // engine hog % to suspend
  private static final double HEAP_THROTTLE = 25.0;  // free heap % to start throttling
  private static final double HEAP_SUSPEND  = 12.0;  // free heap % to suspend

  private static final long HEARTBEAT_SUSPENDED_MS = 30_000;   // "paused, not dead"
  private static final long HEARTBEAT_LIVENESS_MS  = 300_000;  // "alive" on a quiet station
  private static final long WRITE_STALL_MS         = 30_000;   // half-open write watchdog

  enum State { NORMAL, THROTTLING, SUSPENDED }

  private final BSiemForwarderService svc;
  private volatile State state = State.NORMAL;
  private long lastHeartbeat;

  // crude engine-hog estimate: compare wall time to scheduled tick period
  private long lastTickWall;

  private Clock.Ticket ticket;

  SelfThrottleMonitor(BSiemForwarderService svc) { this.svc = svc; }

  void start()
  {
    lastTickWall = System.currentTimeMillis();
    // Sample every 2s, dispatched through the service's throttleTick action
    // slot (Clock requires a real Action).
    ticket = Clock.schedulePeriodically(svc, BRelTime.makeSeconds(2),
                                        BSiemForwarderService.throttleTick, null);
  }

  void stop()
  {
    // Clock tickets do NOT auto-cancel with the service; cancel explicitly so
    // the tick can't keep firing into a stopped service.
    if (ticket != null) { ticket.cancel(); ticket = null; }
  }

  boolean isThrottling() { return state != State.NORMAL; }
  boolean isSuspended()  { return state == State.SUSPENDED; }

  /** Called on the clock every ~2s. */
  void tick()
  {
    double hog  = sampleEngineHogPct();
    double heap = sampleFreeHeapPct();

    State next;
    if (hog >= HOG_SUSPEND || heap <= HEAP_SUSPEND)       next = State.SUSPENDED;
    else if (hog >= HOG_THROTTLE || heap <= HEAP_THROTTLE) next = State.THROTTLING;
    else                                                   next = State.NORMAL;

    if (next != state)
    {
      log.message("SIEM forwarder self-throttle: " + state + " -> " + next
        + " (hog=" + fmt(hog) + "% freeHeap=" + fmt(heap) + "%)");
      state = next;
    }

    // Unstick the worker if a write to a half-open peer has stalled.
    ForwardWorker w = svc.worker();
    if (w != null) w.abortStalledWrite(WRITE_STALL_MS);

    // Heartbeat: fast while suspended ("paused, not dead"), slow otherwise
    // ("alive" — lets the SIEM tell a quiet station from a dead module).
    long now = System.currentTimeMillis();
    long interval = (state == State.SUSPENDED) ? HEARTBEAT_SUSPENDED_MS
                                               : HEARTBEAT_LIVENESS_MS;
    if (now - lastHeartbeat > interval)
    {
      String msg = (state == State.SUSPENDED)
          ? "forwarding suspended: JACE under load (hog=" + fmt(hog) + "% freeHeap=" + fmt(heap) + "%)"
          : "forwarder alive (state=" + state + " hog=" + fmt(hog) + "% freeHeap=" + fmt(heap) + "%)";
      svc.offer(SiemEvent.heartbeat(msg, now));
      lastHeartbeat = now;
    }

    svc.refreshTelemetry();
  }

  /** Should this event be allowed through given current throttle state? */
  boolean admits(SiemEvent e)
  {
    switch (state)
    {
      case SUSPENDED:  return e.isHeartbeat();
      case THROTTLING: return e.severity <= 4 || e.isHeartbeat(); // warn+ only
      default:         return true;
    }
  }

  // -- sampling --------------------------------------------------------------

  /**
   * Estimate engine hog. A precise value is available from the station's
   * EngineWatchdog / SysManager diagnostics; here we approximate from clock
   * jitter (how late our 2s tick actually fired) as a dependency-free proxy.
   */
  private double sampleEngineHogPct()
  {
    long now = System.currentTimeMillis();
    long elapsed = now - lastTickWall;
    lastTickWall = now;
    long expected = 2000;
    double jitter = Math.max(0, elapsed - expected);
    return Math.min(100.0, (jitter / expected) * 100.0);
    // Replace with: ((BEngineWatchdogService)Sys.getService(...)).getEngineHog()
    // for an authoritative reading on your target build.
  }

  private double sampleFreeHeapPct()
  {
    Runtime rt = Runtime.getRuntime();
    long max = rt.maxMemory();
    long used = rt.totalMemory() - rt.freeMemory();
    long free = max - used;
    return (free * 100.0) / max;
  }

  private static String fmt(double d) { return String.format("%.1f", d); }
}
