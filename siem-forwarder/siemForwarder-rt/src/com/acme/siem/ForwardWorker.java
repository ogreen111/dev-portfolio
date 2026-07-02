package com.acme.siem;

import javax.baja.log.Log;
import javax.net.SocketFactory;
import javax.net.ssl.SSLParameters;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;

import java.io.BufferedOutputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

/**
 * ForwardWorker
 * -------------
 * The ONLY thread in this module that touches the network. It owns:
 *   - the BoundedEventQueue (drop-oldest backpressure)
 *   - the TLS/TCP socket to the SIEM, with reconnect-and-backoff
 *   - the sent/dropped counters
 *
 * Event handlers (RideAlongSubscriber, alarm/audit hooks) call enqueue() and
 * return immediately. They never format, never block, never see a socket.
 *
 * The thread runs at BELOW-normal OS priority so the JVM scheduler favors the
 * Niagara engine/driver threads if the CPU is ever contended.
 *
 * Socket state is worker-thread-confined with two deliberate exceptions, both
 * of which exist to UNSTICK a worker blocked in a socket write (Java blocking
 * sockets have no write timeout): stop() and abortStalledWrite() may close the
 * socket out from under the worker. The worker sees the resulting IOException
 * and either exits (stop) or reconnects with backoff (stall).
 */
final class ForwardWorker implements Runnable
{
  private static final Log log = Log.getLog("siemForwarder");

  private final BSiemForwarderService svc;
  private final BoundedEventQueue queue;
  private final SyslogFormatter fmt = new SyslogFormatter();

  private volatile boolean running;
  private volatile boolean connected;
  private volatile long    sent;
  private Thread thread;

  // socket state (worker-thread-confined; see class comment for the exceptions)
  private volatile Socket socket;
  private volatile OutputStream out;
  private long backoffMs = 1000;                 // grows to a cap on repeated failure
  private static final long BACKOFF_MAX = 60_000;

  // wall-clock start of the in-flight write, 0 when no write is in flight;
  // read by the monitor tick to detect a half-open-peer write stall
  private volatile long writeStartMs;

  // drop-report bookkeeping (worker thread only)
  private long lastDropReport;
  private long reportedDrops;
  private static final long DROP_REPORT_INTERVAL_MS = 30_000;

  ForwardWorker(BSiemForwarderService svc)
  {
    this.svc = svc;
    this.queue = new BoundedEventQueue(svc.getQueueCapacity());
  }

  // -- public (called from event threads) -----------------------------------

  void enqueue(SiemEvent e) { queue.offer(e); }
  void countDrop()          { queue.countExternalDrop(); }

  int  depth()       { return queue.size(); }
  long dropped()     { return queue.dropped(); }
  long sent()        { return sent; }
  boolean isConnected() { return connected; }

  // -- lifecycle -------------------------------------------------------------

  void start()
  {
    running = true;
    thread = new Thread(this, "siemForwarder-worker");
    thread.setDaemon(true);
    thread.setPriority(Thread.MIN_PRIORITY + 1);   // stay out of the engine's way
    thread.start();
  }

  void stop()
  {
    running = false;
    if (thread != null) thread.interrupt();
    closeSocket();          // cross-thread close: unblocks a worker stuck in write
  }

  /**
   * Called from the SelfThrottleMonitor's clock tick. A half-open SIEM peer
   * (dead but not RST) can leave the worker blocked in write()/flush() until
   * the OS TCP timeout — minutes, far beyond the 60 s backoff cap. If a single
   * write has been in flight longer than maxMs, close the socket so the worker
   * takes its normal reconnect-with-backoff path. Never touches the engine.
   */
  void abortStalledWrite(long maxMs)
  {
    long start = writeStartMs;
    if (start != 0 && System.currentTimeMillis() - start > maxMs)
    {
      log.warning("SIEM write stalled > " + maxMs + " ms; closing socket to unblock worker");
      closeSocket();
    }
  }

  // -- the loop --------------------------------------------------------------

  @Override
  public void run()
  {
    while (running)
    {
      try
      {
        if (!connected) { connect(); }

        // Surface an accumulated-drops summary on EVERY pass, not just idle
        // ticks: sustained saturation (exactly when drops happen) never has an
        // idle tick, so an idle-only report would starve.
        maybeReportDrops();

        SiemEvent e = queue.poll(1000);
        if (e == null) continue;

        writeLine(fmt.format(e));
        sent++;
      }
      catch (InterruptedException ie)
      {
        // stop() was called
        break;
      }
      catch (Exception ex)
      {
        // Any I/O failure: drop the connection and back off. We NEVER let a SIEM
        // problem propagate; worst case events pile into the bounded queue and
        // the oldest are shed.
        log.warning("SIEM socket error, will reconnect: " + ex);
        closeSocket();
        sleepBackoff();
      }
    }
    closeSocket();
  }

  /** Report new drops at most every 30 s, regardless of queue pressure. */
  private void maybeReportDrops() throws Exception
  {
    long d = queue.dropped();
    long now = System.currentTimeMillis();
    if (d != reportedDrops && (now - lastDropReport) > DROP_REPORT_INTERVAL_MS)
    {
      writeLine(fmt.format(SiemEvent.dropReport(d - reportedDrops, now)));
      reportedDrops = d;
      lastDropReport = now;
    }
  }

  // -- socket handling -------------------------------------------------------

  private void connect() throws Exception
  {
    SocketFactory sf = svc.getUseTls()
        ? SSLSocketFactory.getDefault()
        : SocketFactory.getDefault();

    Socket s = sf.createSocket();
    if (s instanceof SSLSocket)
    {
      // Raw SSL sockets do NOT verify the peer hostname by default — without
      // this, any certificate the trust store accepts is valid for ANY host
      // and the link is MITM-able. Endpoint identification checks the cert
      // against the host we dialed.
      SSLSocket ssl = (SSLSocket)s;
      SSLParameters params = ssl.getSSLParameters();
      params.setEndpointIdentificationAlgorithm("HTTPS");
      ssl.setSSLParameters(params);
      // BIND POINT: SSLSocketFactory.getDefault() trusts the JVM-default
      // (javax.net.ssl) store. To anchor trust in the Niagara platform
      // certificate store instead, obtain the SSLContext from the platform's
      // certificate manager API on the target build and create the factory
      // from it.
    }
    s.connect(new InetSocketAddress(svc.getSiemHost(), svc.getSiemPort()), 5000);
    s.setSoTimeout(0);
    s.setTcpNoDelay(true);
    this.socket = s;
    this.out = new BufferedOutputStream(s.getOutputStream(), 8192);
    this.connected = true;
    this.backoffMs = 1000;                        // reset on success
    log.message("SIEM connected: " + svc.getSiemHost() + ":" + svc.getSiemPort());
  }

  /** RFC 5425 octet-counting frame: "<len> <syslog-msg>". */
  private void writeLine(String syslogMsg) throws Exception
  {
    byte[] body = syslogMsg.getBytes(StandardCharsets.UTF_8);
    byte[] frame = (body.length + " ").getBytes(StandardCharsets.US_ASCII);
    writeStartMs = System.currentTimeMillis();
    try
    {
      out.write(frame);
      out.write(body);
      out.flush();
    }
    finally
    {
      writeStartMs = 0;
    }
  }

  private void closeSocket()
  {
    connected = false;
    Socket s = socket; OutputStream o = out;
    socket = null; out = null;
    // Close the socket first: Socket.close() is async-safe and unblocks a
    // stuck write; closing the buffered stream first could itself block on a
    // flush to the dead peer.
    try { if (s != null) s.close(); } catch (Exception ignore) {}
    try { if (o != null) o.close(); } catch (Exception ignore) {}
  }

  private void sleepBackoff()
  {
    try { Thread.sleep(backoffMs); } catch (InterruptedException ie) { Thread.currentThread().interrupt(); }
    backoffMs = Math.min(backoffMs * 2, BACKOFF_MAX);
  }
}
