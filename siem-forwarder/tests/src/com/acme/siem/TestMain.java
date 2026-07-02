package com.acme.siem;

/**
 * Tiny zero-dependency test harness. Lives in com.acme.siem because the
 * classes under test are package-private. Run via tests/run-tests.sh, which
 * compiles the two pure-Java production classes plus these tests with plain
 * javac — no Niagara dev bundle or Gradle toolchain required.
 */
final class TestMain
{
  private static int passed;
  private static int failed;

  public static void main(String[] args) throws Exception
  {
    BoundedEventQueueTest.run();
    SiemEventTest.run();

    System.out.println();
    System.out.println(passed + " passed, " + failed + " failed");
    if (failed > 0) System.exit(1);
  }

  static void check(String label, boolean ok)
  {
    if (ok) { passed++; System.out.println("  PASS  " + label); }
    else    { failed++; System.out.println("  FAIL  " + label); }
  }

  static void checkEq(String label, Object expected, Object actual)
  {
    boolean ok = expected == null ? actual == null : expected.equals(actual);
    if (ok) { passed++; System.out.println("  PASS  " + label); }
    else
    {
      failed++;
      System.out.println("  FAIL  " + label + " — expected " + expected + ", got " + actual);
    }
  }
}
