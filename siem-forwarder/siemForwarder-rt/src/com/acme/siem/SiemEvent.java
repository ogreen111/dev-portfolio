package com.acme.siem;

/**
 * A lightweight, immutable value object describing one thing worth telling the
 * SIEM about. Deliberately a plain POJO (no Baja slots) so it can be built on
 * the event thread in microseconds and handed to the worker without touching
 * the component tree off-thread.
 */
final class SiemEvent
{
  enum Kind { POINT, ALARM, AUDIT, HEARTBEAT, DROP_REPORT }

  final Kind    kind;
  final String  source;     // e.g. "Drivers/Bacnet/MSTP1/AHU3/SupplyTemp"
  final String  message;    // human/CEF-ready payload
  final int     severity;   // syslog severity 0..7
  final long    tsMillis;   // event time (station clock)

  private SiemEvent(Kind kind, String source, String message, int severity, long tsMillis)
  {
    this.kind = kind;
    this.source = source == null ? "-" : source;
    this.message = message == null ? "" : message;
    this.severity = severity;
    this.tsMillis = tsMillis;
  }

  boolean isHeartbeat() { return kind == Kind.HEARTBEAT; }

  static SiemEvent point(String source, String msg, int sev, long ts)
  { return new SiemEvent(Kind.POINT, source, msg, sev, ts); }

  static SiemEvent alarm(String source, String msg, int sev, long ts)
  { return new SiemEvent(Kind.ALARM, source, msg, sev, ts); }

  static SiemEvent audit(String source, String msg, long ts)
  { return new SiemEvent(Kind.AUDIT, source, msg, 5 /*notice*/, ts); }

  static SiemEvent heartbeat(String msg, long ts)
  { return new SiemEvent(Kind.HEARTBEAT, "siemForwarder", msg, 6 /*info*/, ts); }

  static SiemEvent dropReport(long dropped, long ts)
  { return new SiemEvent(Kind.DROP_REPORT, "siemForwarder",
      "gap: " + dropped + " events dropped due to backpressure/throttle", 4 /*warn*/, ts); }
}
