package com.acme.siem;

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

  // Points we're currently riding along on, and the last monotonic tick we
  // forwarded each (for the per-point min-interval deadband). Doubles as the
  // attached-set; keyed by Handle so it survives renames.
  private final ConcurrentHashMap<Handle,Long> lastSentByPoint = new ConcurrentHashMap<>();

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
    Set<Handle> present = new HashSet<>();
    for (BControlPoint pt : findPoints(root))
    {
      Handle h = pt.getHandle();
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
      Handle h = pt.getHandle();
      if (h == null) return;

      // Per-point min-interval deadband: protect the queue from a chattering
      // point on a fast trunk. Enforced here, at the source, before enqueue.
      // Deadband arithmetic uses the monotonic tick clock; the event itself is
      // stamped with wall-clock time (the SIEM needs real timestamps).
      long nowTicks = Clock.ticks();
      Long last = lastSentByPoint.get(h);
      long minGap = svc.getMinIntervalMs();
      if (last != null && last != 0L && (nowTicks - last) < minGap) return;
      lastSentByPoint.put(h, nowTicks);

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
    // Attach listeners to AlarmService and AuditHistoryService here. These are
    // station-internal and never generate RS-485 traffic, so no ride-along gate
    // is needed — forward everything (subject to the same bounded queue).
    //
    //   BAlarmService alarms = (BAlarmService)Sys.getService(BAlarmService.TYPE);
    //   alarms.getAlarmClass(...).addAlarmRecipient(new BSiemAlarmRecipient(svc));
    //
    //   BAuditHistoryService audit = ...
    //   audit.subscribe(auditListener -> svc.offer(SiemEvent.audit(...)));
    //
    // Left as wiring points so the skeleton stays framework-version-agnostic.
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
