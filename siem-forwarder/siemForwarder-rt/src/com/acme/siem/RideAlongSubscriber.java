package com.acme.siem;

import javax.baja.alarm.BAlarmClass;
import javax.baja.alarm.BAlarmRecord;
import javax.baja.alarm.BAlarmService;
import javax.baja.control.BControlPoint;
import javax.baja.log.Log;
import javax.baja.status.BStatusValue;
import javax.baja.sys.*;

import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * RideAlongSubscriber
 * -------------------
 * The heart of the "do not disturb the field bus" constraint.
 *
 * THE TRAP WE ARE AVOIDING:
 *   In Niagara, calling Subscriber.subscribe(point) forces that proxy point into
 *   the driver's active poll set. On an RS-485 trunk (BACnet MS/TP, Modbus RTU)
 *   that adds real wire traffic and can perturb token timing / poll cycles. A
 *   "monitor" that subscribes points is therefore NOT passive.
 *
 * THE RIDE-ALONG RULE:
 *   We only ever attach to points that are ALREADY subscribed by someone else
 *   (a Px graphic, a history extension, control logic). Niagara ref-counts
 *   subscriptions, so joining an existing one adds ZERO polls to the trunk. When
 *   the last *external* subscriber goes away, we let go too — we never keep a
 *   point alive on our own account.
 *
 * We periodically re-scan (on the app clock, cheaply) to pick up newly-active
 * points and release ones that went idle. COV callbacks come in via a standard
 * Subscriber; each callback just builds a SiemEvent and hands it to the service,
 * which enqueues it on the bounded queue. No I/O here.
 *
 * Threading: rescan() runs on the app-clock tick; onCov() runs on COV event
 * threads. The attach/deadband map is therefore a ConcurrentHashMap — it is the
 * one piece of state both touch.
 */
final class RideAlongSubscriber
{
  private static final Log log = Log.getLog("siemForwarder");

  private final BSiemForwarderService svc;

  // Our subscriber. We only add points that are already externally subscribed.
  private final Subscriber sub = new Subscriber()
  {
    @Override public void event(BComponentEvent e) { onCov(e); }
  };

  // Points we're currently riding along on, and the last monotonic nanoTime we
  // forwarded each (for the per-point min-interval deadband). Doubles as the
  // attached-set; keyed by the component handle. BComponent.getHandle() returns
  // an opaque, rename-stable Object (there is no javax.baja.sys.Handle type), so
  // the key type is Object.
  private final ConcurrentHashMap<Object,Long> lastSentByPoint = new ConcurrentHashMap<>();

  // Dedicated subscriber for alarm-class topics. Kept separate from `sub` so the
  // ride-along point logic and the alarm logic never tangle in one event().
  // Transient: attached in start(), dropped in stop(); nothing written to config.
  private Subscriber alarmSub;

  private Clock.Ticket ticket;
  private boolean alarmAuditHooked;

  RideAlongSubscriber(BSiemForwarderService svc) { this.svc = svc; }

  void start()
  {
    // Scan every 10s. This walk is in-memory (no polling), so it's cheap and
    // never touches the RS-485 wire. Dispatched through the service's
    // rideAlongRescan action slot (Clock requires a real Action).
    ticket = Clock.schedulePeriodically(svc, BRelTime.makeSeconds(10),
                                        BSiemForwarderService.rideAlongRescan, null);
    hookAlarmAndAudit();
  }

  void stop()
  {
    if (ticket != null) { ticket.cancel(); ticket = null; }
    try { sub.unsubscribeAll(); } catch (Exception ignore) {}
    if (alarmSub != null)
    {
      try { alarmSub.unsubscribeAll(); } catch (Exception ignore) {}
      alarmSub = null;
    }
    lastSentByPoint.clear();
  }

  // ==========================================================================
  //  Periodic ride-along scan
  // ==========================================================================

  /**
   * Called on each scan tick. Reconcile our attached set with "what is currently
   * subscribed by someone else."
   */
  void rescan()
  {
    if (!svc.getForwardPoints()) { detachAll(); return; }

    BObject o = svc.getNetworkOrd().resolve(svc, null).get();
    if (!(o instanceof BComponent)) return;
    BComponent root = (BComponent)o;

    // Walk the driver subtree. For each control point:
    Set<Object> present = new HashSet<>();
    for (BControlPoint pt : findPoints(root))
    {
      Object h = pt.getHandle();
      if (h == null) continue;                  // not mounted; nothing to ride
      present.add(h);

      boolean externallyActive = isExternallySubscribed(pt);
      boolean weAreAttached    = lastSentByPoint.containsKey(h);

      if (externallyActive && !weAreAttached)
      {
        // Ride along: join the existing subscription (adds no poll load).
        sub.subscribe(pt);
        lastSentByPoint.put(h, 0L);
      }
      else if (!externallyActive && weAreAttached)
      {
        // The external interest is gone — release so we don't keep it polled.
        sub.unsubscribe(pt);
        lastSentByPoint.remove(h);
      }
    }

    // Points deleted from the station never reappear in the walk; drop their
    // entries so the map can't grow without bound under point churn.
    lastSentByPoint.keySet().retainAll(present);
  }

  /**
   * True only if some component OTHER than us is holding this point subscribed.
   * isSubscribed() alone can't tell our own subscription from an external one
   * (it stays true once we attach), so we inspect the subscriber list and
   * require at least one entry that is not our own Subscriber instance.
   */
  private boolean isExternallySubscribed(BControlPoint pt)
  {
    Subscriber[] subs = pt.getSubscribers();
    if (subs == null) return false;
    for (Subscriber s : subs)
    {
      if (s != sub) return true;                // someone else still wants it
    }
    return false;                               // nobody, or only us -> release
  }

  // ==========================================================================
  //  COV callback -> SiemEvent (no I/O, just enqueue)
  // ==========================================================================

  private void onCov(BComponentEvent e)
  {
    try
    {
      BComponent c = e.getSourceComponent();
      if (!(c instanceof BControlPoint)) return;
      BControlPoint pt = (BControlPoint)c;
      Object h = pt.getHandle();
      if (h == null) return;

      // Per-point min-interval deadband: protect the queue from a chattering
      // point on a fast trunk. Enforced here, at the source, before enqueue.
      // Deadband arithmetic uses System.nanoTime() (unambiguously nanoseconds
      // and monotonic); the event itself is stamped with wall-clock time (the
      // SIEM needs real timestamps). We avoid Clock.ticks() here: its unit is
      // not documented (a sibling Clock.nanoTicks() exists), so mixing it with
      // the millisecond minInterval risked an ~1e6 error.
      long nowNs = System.nanoTime();
      Long last = lastSentByPoint.get(h);
      long minGapNs = svc.getMinIntervalMs() * 1_000_000L;
      if (last != null && last != 0L && (nowNs - last) < minGapNs) return;
      lastSentByPoint.put(h, nowNs);

      BStatusValue out = pt.getOutStatusValue();
      String src = pt.getSlotPath().toString();
      String msg = "value=" + out.toString(null)
                 + " status=" + out.getStatus().toString(null);
      int sev = out.getStatus().isValid() ? 6 /*info*/ : 4 /*warning*/;

      svc.offer(SiemEvent.point(src, msg, sev, System.currentTimeMillis()));
    }
    catch (Exception ex)
    {
      log.trace("cov handling error: " + ex);
    }
  }

  // ==========================================================================
  //  Alarm + audit hooks (decoupled from the field bus entirely)
  // ==========================================================================

  private void hookAlarmAndAudit()
  {
    if (alarmAuditHooked) return;
    alarmAuditHooked = true;
    // Alarm classes and the audit history are station-internal and never
    // generate RS-485 traffic, so no ride-along gate is needed — forward
    // everything (subject to the same bounded queue and self-throttle).
    if (svc.getForwardAlarms()) subscribeAlarms();

    // AUDIT is deliberately NOT forwarded by this module. A transient seam does
    // exist (watch the `lastRecord` Property on BAuditHistoryService and its
    // SecurityAuditHistorySource child), but reading the record's fields
    // requires the com.tridium.history.audit.* implementation classes — internal
    // API, not the stable javax.baja contract, and unwanted coupling inside the
    // accreditation boundary. Niagara's built-in remote syslog (4.10+) already
    // exports audit/platform logs cleanly over RFC 5424, so audit is left to it
    // — keeping this module's custom-code surface to points + alarms only. The
    // `forwardAudit` config slot stays for operators who wire an external audit
    // path, but this module does not act on it.
  }

  /**
   * Transiently listen for alarms. We attach `alarmSub` to every alarm class and
   * catch its public `alarm` Topic firing. This writes NOTHING to the config DB
   * (unlike parenting a BAlarmRecipient under each class), which keeps the
   * module's non-interference / CM footprint minimal. Verified against the 4.10
   * and 4.15 API: BAlarmService.getAlarmClasses() -> BAlarmClass[], BAlarmClass
   * has a public `alarm` Topic, and a TOPIC_FIRED BComponentEvent carries the
   * BAlarmRecord via getValue().
   */
  private void subscribeAlarms()
  {
    // Fail-open: alarm forwarding is best-effort and must NEVER abort the
    // service (which would kill point forwarding too). Sys.getService(Type)
    // THROWS ServiceNotFoundException when no alarm service is registered, so we
    // use getServices() (returns an empty array, never throws) and wrap the
    // whole setup so any surprise just disables alarms.
    try
    {
      BComponent[] found = Sys.getServices(BAlarmService.TYPE);
      if (found == null || found.length == 0)
      {
        log.trace("no AlarmService; alarm forwarding disabled");
        return;
      }
      BAlarmService as = (BAlarmService)found[0];

      alarmSub = new Subscriber()
      {
        @Override public void event(BComponentEvent e) { onAlarm(e); }
      };
      for (BAlarmClass ac : as.getAlarmClasses())
      {
        if (ac != null) alarmSub.subscribe(ac);
      }
    }
    catch (Exception ex)
    {
      // Release any classes already attached before the failure, otherwise the
      // subscriber would keep firing onAlarm() after we drop the reference and
      // stop() could no longer clean it up.
      log.warning("alarm forwarding disabled (setup failed): " + ex);
      if (alarmSub != null)
      {
        try { alarmSub.unsubscribeAll(); } catch (Exception ignore) {}
        alarmSub = null;
      }
    }
  }

  /** Alarm-class topic callback -> SiemEvent (no I/O, just enqueue). */
  private void onAlarm(BComponentEvent e)
  {
    try
    {
      // Only the primary `alarm` topic. Skip escalatedAlarm1/2/3 (duplicates of
      // the same record) and any non-topic event on the class.
      if (e.getId() != BComponentEvent.TOPIC_FIRED) return;
      if (!"alarm".equals(e.getSlotName())) return;

      BValue v = e.getValue();
      if (!(v instanceof BAlarmRecord)) return;
      BAlarmRecord r = (BAlarmRecord)v;

      String src = r.getSource() != null ? r.getSource().toString() : "-";
      // Niagara alarm priority is 1 (highest) .. 255 (lowest); map the urgent
      // half to syslog error, the rest to warning.
      int sev = r.getPriority() <= 127 ? 3 /*error*/ : 4 /*warning*/;
      String msg = "alarm class=" + r.getAlarmClass()
                 + " transition=" + r.getSourceState()
                 + " priority=" + r.getPriority()
                 + " ack=" + r.getAckState()
                 + " uuid=" + r.getUuid();
      long ts = r.getTimestamp() != null ? r.getTimestamp().getMillis()
                                         : System.currentTimeMillis();

      svc.offer(SiemEvent.alarm(src, msg, sev, ts));
    }
    catch (Exception ex)
    {
      log.trace("alarm handling error: " + ex);
    }
  }

  // ==========================================================================
  //  Helpers
  // ==========================================================================

  private java.util.List<BControlPoint> findPoints(BComponent root)
  {
    java.util.ArrayList<BControlPoint> list = new java.util.ArrayList<>();
    collect(root, list);
    return list;
  }

  private void collect(BComponent c, java.util.List<BControlPoint> out)
  {
    if (c instanceof BControlPoint) out.add((BControlPoint)c);
    for (BComponent kid : c.getChildComponents()) collect(kid, out);
  }

  private void detachAll()
  {
    try { sub.unsubscribeAll(); } catch (Exception ignore) {}
    lastSentByPoint.clear();
  }
}
