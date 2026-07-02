package com.acme.siem;

import static com.acme.siem.TestMain.check;
import static com.acme.siem.TestMain.checkEq;

/** Factory-method contracts: kind, severity, and null-source/message defaults. */
final class SiemEventTest
{
  static void run()
  {
    System.out.println("SiemEventTest");
    point_passesThroughAllFields();
    alarm_kindAndSeverity();
    audit_fixedSeverity5();
    heartbeat_fixedSourceAndSeverity6();
    dropReport_fixedSourceSeverity4AndCountInMessage();
    nullSource_defaultsToDash();
    nullMessage_defaultsToEmpty();
  }

  private static void point_passesThroughAllFields()
  {
    SiemEvent e = SiemEvent.point("Drivers/Bacnet/AHU3/SupplyTemp", "72.4 ok", 6, 1234L);
    checkEq("point kind", SiemEvent.Kind.POINT, e.kind);
    checkEq("point source", "Drivers/Bacnet/AHU3/SupplyTemp", e.source);
    checkEq("point message", "72.4 ok", e.message);
    checkEq("point severity passthrough", 6, e.severity);
    checkEq("point tsMillis passthrough", 1234L, e.tsMillis);
    check("point is not a heartbeat", !e.isHeartbeat());
  }

  private static void alarm_kindAndSeverity()
  {
    SiemEvent e = SiemEvent.alarm("src", "offnormal", 2, 5L);
    checkEq("alarm kind", SiemEvent.Kind.ALARM, e.kind);
    checkEq("alarm severity passthrough", 2, e.severity);
  }

  private static void audit_fixedSeverity5()
  {
    SiemEvent e = SiemEvent.audit("src", "user login", 7L);
    checkEq("audit kind", SiemEvent.Kind.AUDIT, e.kind);
    checkEq("audit severity fixed at 5 (notice)", 5, e.severity);
  }

  private static void heartbeat_fixedSourceAndSeverity6()
  {
    SiemEvent e = SiemEvent.heartbeat("alive", 9L);
    checkEq("heartbeat kind", SiemEvent.Kind.HEARTBEAT, e.kind);
    checkEq("heartbeat source fixed", "siemForwarder", e.source);
    checkEq("heartbeat severity fixed at 6 (info)", 6, e.severity);
    check("heartbeat isHeartbeat()", e.isHeartbeat());
  }

  private static void dropReport_fixedSourceSeverity4AndCountInMessage()
  {
    SiemEvent e = SiemEvent.dropReport(17L, 11L);
    checkEq("dropReport kind", SiemEvent.Kind.DROP_REPORT, e.kind);
    checkEq("dropReport source fixed", "siemForwarder", e.source);
    checkEq("dropReport severity fixed at 4 (warn)", 4, e.severity);
    check("dropReport message carries the drop count", e.message.contains("17"));
    check("dropReport message mentions dropping", e.message.contains("dropped"));
  }

  private static void nullSource_defaultsToDash()
  {
    SiemEvent e = SiemEvent.point(null, "msg", 6, 1L);
    checkEq("null source defaults to \"-\"", "-", e.source);
  }

  private static void nullMessage_defaultsToEmpty()
  {
    SiemEvent e = SiemEvent.point("src", null, 6, 1L);
    checkEq("null message defaults to empty string", "", e.message);
  }
}
