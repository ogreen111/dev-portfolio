package com.acme.siem;

import javax.baja.sys.Sys;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;

/**
 * SyslogFormatter
 * ---------------
 * Renders a SiemEvent as an RFC 5424 syslog message. Every major SIEM
 * (Splunk, QRadar, Sentinel, Elastic, Chronicle) ingests 5424 natively, so this
 * keeps the JACE side vendor-neutral. Swap format() for a CEF/LEEF builder if
 * your SIEM prefers it — the rest of the module is unaffected.
 *
 * Format:
 *   <PRI>1 TIMESTAMP HOST APP PROCID [SD] MSG    (MSGID = event kind)
 *
 * PRI = facility*8 + severity. We use facility 13 (log audit) for AUDIT events
 * and facility 16 (local0) for everything else.
 *
 * Thread-confinement: instances are used only by the single ForwardWorker
 * thread (SimpleDateFormat is not thread-safe).
 */
final class SyslogFormatter
{
  private static final int FAC_AUDIT = 13;
  private static final int FAC_LOCAL0 = 16;

  private final SimpleDateFormat ts;
  private final String host;
  private final String station;

  SyslogFormatter()
  {
    ts = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
    ts.setTimeZone(TimeZone.getTimeZone("UTC"));
    host = hdr(safeHostname());
    station = hdr(safeStationName());
  }

  String format(SiemEvent e)
  {
    int facility = (e.kind == SiemEvent.Kind.AUDIT) ? FAC_AUDIT : FAC_LOCAL0;
    int pri = facility * 8 + clampSeverity(e.severity);

    String app   = "niagara-siem";
    String msgid = e.kind.name();

    // Structured data: machine-parseable fields the SIEM can index on.
    String sd = "[niagara@32473"
        + " src=\"" + esc(e.source) + "\""
        + " kind=\"" + e.kind.name() + "\""
        + " station=\"" + esc(station) + "\"]";

    return "<" + pri + ">1 "
         + ts.format(new Date(e.tsMillis)) + " "
         + host + " "
         + app + " "
         + station + " "
         + msgid + " "
         + sd + " "
         + e.message;
  }

  private static int clampSeverity(int s) { return (s < 0) ? 0 : (s > 7 ? 7 : s); }

  private static String esc(String s)
  {
    if (s == null) return "-";
    return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("]", "\\]");
  }

  /**
   * RFC 5424 header fields are space-delimited PRINTUSASCII; a station name
   * with a space (or any control/non-ASCII char) would corrupt the header.
   * Sanitize to '_' and fall back to NILVALUE when empty.
   */
  private static String hdr(String s)
  {
    if (s == null || s.isEmpty()) return "-";
    return s.replaceAll("[^\\x21-\\x7e]", "_");
  }

  private static String safeHostname()
  {
    try { return java.net.InetAddress.getLocalHost().getHostName(); }
    catch (Exception e) { return "jace"; }
  }

  private static String safeStationName()
  {
    // getStation() is static on Sys, not an instance method on the service.
    try { return Sys.getStation() != null ? Sys.getStation().getName() : "station"; }
    catch (Exception e) { return "station"; }
  }
}
