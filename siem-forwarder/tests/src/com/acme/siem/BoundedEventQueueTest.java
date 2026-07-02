package com.acme.siem;

import static com.acme.siem.TestMain.check;
import static com.acme.siem.TestMain.checkEq;

/** SDD test cases T1 and T2, plus poll/drop-counter contract checks. */
final class BoundedEventQueueTest
{
  static void run() throws Exception
  {
    System.out.println("BoundedEventQueueTest");
    t1_dropOldestUnderOverflow();
    t1_capacityFloorOf16();
    t2_offerNeverBlocks();
    poll_returnsNullOnTimeout();
    poll_returnsQueuedEventImmediately();
    offer_wakesBlockedPoller();
    countExternalDrop_incrementsCounterOnly();
  }

  /**
   * T1 — Drop-oldest under overflow. Enqueue > capacity with no consumer;
   * the newest CAP events survive in FIFO order, the oldest are shed, and the
   * dropped counter is exact.
   */
  private static void t1_dropOldestUnderOverflow() throws InterruptedException
  {
    final int cap = 32;
    final int total = 100;
    BoundedEventQueue q = new BoundedEventQueue(cap);
    for (int i = 0; i < total; i++)
      q.offer(SiemEvent.point("p", "m" + i, 6, i));

    checkEq("T1 size capped at capacity", cap, q.size());
    checkEq("T1 dropped counter exact", (long) (total - cap), q.dropped());

    boolean newestRetained = true;
    for (int i = total - cap; i < total; i++)
    {
      SiemEvent e = q.poll(1);
      if (e == null || e.tsMillis != i) { newestRetained = false; break; }
    }
    check("T1 newest " + cap + " retained in FIFO order, oldest shed", newestRetained);
    checkEq("T1 queue drained after readback", 0, q.size());
  }

  /** The constructor clamps capacity to a floor of 16. */
  private static void t1_capacityFloorOf16()
  {
    BoundedEventQueue q = new BoundedEventQueue(1);
    for (int i = 0; i < 20; i++)
      q.offer(SiemEvent.point("p", "m", 6, i));
    checkEq("capacity floor: size is 16 for requested capacity 1", 16, q.size());
    checkEq("capacity floor: dropped counts overflow past 16", 4L, q.dropped());
  }

  /**
   * T2 — offer() never blocks. Flood offers with no consumer (queue saturated,
   * dropping on every call) and assert every call returns in well under 1 ms.
   * Timing is retried a few times so a stray GC pause can't fail the suite.
   */
  private static void t2_offerNeverBlocks()
  {
    final long limitNs = 1_000_000L; // 1 ms
    final int floods = 100_000;
    long best = Long.MAX_VALUE;
    for (int attempt = 0; attempt < 3 && best >= limitNs; attempt++)
    {
      BoundedEventQueue q = new BoundedEventQueue(1024);
      SiemEvent e = SiemEvent.point("p", "m", 6, 0);
      long max = 0;
      for (int i = 0; i < floods; i++)
      {
        long t0 = System.nanoTime();
        q.offer(e);
        long dt = System.nanoTime() - t0;
        if (dt > max) max = dt;
      }
      if (max < best) best = max;
    }
    check("T2 offer() never blocks: worst of " + floods + " saturated offers = "
        + (best / 1000) + "µs (< 1ms)", best < limitNs);
  }

  /** poll() on an empty queue waits up to the timeout, then returns null. */
  private static void poll_returnsNullOnTimeout() throws InterruptedException
  {
    BoundedEventQueue q = new BoundedEventQueue(16);
    long t0 = System.nanoTime();
    SiemEvent e = q.poll(50);
    long elapsedMs = (System.nanoTime() - t0) / 1_000_000;
    check("poll(50) on empty queue returns null", e == null);
    check("poll(50) actually waited (~" + elapsedMs + "ms)", elapsedMs >= 30);
  }

  /** poll() returns an already-queued event without waiting out the timeout. */
  private static void poll_returnsQueuedEventImmediately() throws InterruptedException
  {
    BoundedEventQueue q = new BoundedEventQueue(16);
    q.offer(SiemEvent.alarm("src", "msg", 3, 42));
    long t0 = System.nanoTime();
    SiemEvent e = q.poll(5_000);
    long elapsedMs = (System.nanoTime() - t0) / 1_000_000;
    check("poll returns queued event", e != null && e.tsMillis == 42);
    check("poll did not wait out the timeout (" + elapsedMs + "ms)", elapsedMs < 1_000);
  }

  /** offer() notifies a consumer blocked in poll(). */
  private static void offer_wakesBlockedPoller() throws InterruptedException
  {
    BoundedEventQueue q = new BoundedEventQueue(16);
    final SiemEvent[] got = new SiemEvent[1];
    Thread consumer = new Thread(() -> {
      try { got[0] = q.poll(10_000); }
      catch (InterruptedException ignored) { }
    });
    consumer.start();
    Thread.sleep(100); // let the consumer reach wait()
    q.offer(SiemEvent.heartbeat("hb", 1));
    consumer.join(2_000);
    check("offer wakes a blocked poller",
        !consumer.isAlive() && got[0] != null && got[0].isHeartbeat());
  }

  /** countExternalDrop() bumps the drop counter without touching the queue. */
  private static void countExternalDrop_incrementsCounterOnly()
  {
    BoundedEventQueue q = new BoundedEventQueue(16);
    q.countExternalDrop();
    q.countExternalDrop();
    q.countExternalDrop();
    checkEq("countExternalDrop increments dropped", 3L, q.dropped());
    checkEq("countExternalDrop leaves queue empty", 0, q.size());

    q.offer(SiemEvent.point("p", "m", 6, 0));
    q.countExternalDrop();
    checkEq("external + overflow drops share one counter", 4L, q.dropped());
    checkEq("countExternalDrop does not consume queued events", 1, q.size());
  }
}
