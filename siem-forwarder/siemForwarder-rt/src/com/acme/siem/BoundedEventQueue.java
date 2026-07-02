package com.acme.siem;

import java.util.ArrayDeque;

/**
 * A fixed-capacity, DROP-OLDEST queue.
 *
 * Rationale: the whole point of the non-interference design is that SIEM data
 * is the thing we sacrifice under pressure, never engine time. A blocking queue
 * would let a slow/stalled SIEM socket back-propagate pressure onto the event
 * thread (or grow the heap unbounded). Instead, when we hit capacity we discard
 * the OLDEST event and keep the newest — freshest security state wins — and we
 * increment a drop counter so the gap is visible and reportable to the SIEM.
 *
 * Intentionally tiny and dependency-free. Guarded by its own monitor; producers
 * (event thread) and the single consumer (worker thread) both hold it only for
 * the O(1) enqueue/dequeue, never across I/O.
 */
final class BoundedEventQueue
{
  private final ArrayDeque<SiemEvent> q;
  private final int capacity;
  private long dropped;

  BoundedEventQueue(int capacity)
  {
    this.capacity = Math.max(16, capacity);
    this.q = new ArrayDeque<>(this.capacity);
  }

  /** Non-blocking. Never throws, never waits. Drops oldest if full. */
  synchronized void offer(SiemEvent e)
  {
    if (q.size() >= capacity)
    {
      q.pollFirst();      // shed oldest
      dropped++;
    }
    q.addLast(e);
    notify();             // wake the single consumer
  }

  /** Blocks up to timeoutMs for an event; returns null on timeout. */
  synchronized SiemEvent poll(long timeoutMs) throws InterruptedException
  {
    if (q.isEmpty()) wait(timeoutMs);
    return q.pollFirst();
  }

  synchronized void countExternalDrop() { dropped++; }
  synchronized int  size()    { return q.size(); }
  synchronized long dropped() { return dropped; }

  synchronized void clear() { q.clear(); }
}
