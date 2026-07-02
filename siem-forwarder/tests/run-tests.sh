#!/bin/sh
# Standalone unit-test runner for the pure-Java classes (BoundedEventQueue,
# SiemEvent). Compiles them plus the tests with plain javac and runs the tiny
# harness — no Niagara dev bundle, Gradle, or JUnit jar required.
set -e
cd "$(dirname "$0")/.."

# Locate a working JDK. On macOS, /usr/bin/javac is a stub that fails when no
# JDK is installed, so probe with `javac -version` rather than `command -v`.
find_jdk_bin()
{
  if [ -n "$JAVA_HOME" ] && "$JAVA_HOME/bin/javac" -version >/dev/null 2>&1; then
    echo "$JAVA_HOME/bin"; return 0
  fi
  if javac -version >/dev/null 2>&1 && java -version >/dev/null 2>&1; then
    echo ""; return 0   # PATH works as-is
  fi
  jh=$(/usr/libexec/java_home 2>/dev/null || true)
  if [ -n "$jh" ] && "$jh/bin/javac" -version >/dev/null 2>&1; then
    echo "$jh/bin"; return 0
  fi
  for d in /opt/homebrew/opt/openjdk*/bin /usr/local/opt/openjdk*/bin; do
    if "$d/javac" -version >/dev/null 2>&1; then echo "$d"; return 0; fi
  done
  return 1
}

BIN=$(find_jdk_bin) || {
  echo "error: no JDK found (need javac 8+). Install one, e.g. 'brew install openjdk'." >&2
  exit 1
}
if [ -n "$BIN" ]; then JAVAC="$BIN/javac"; JAVA="$BIN/java"; else JAVAC=javac; JAVA=java; fi

OUT=tests/build
rm -rf "$OUT"
mkdir -p "$OUT"

"$JAVAC" -d "$OUT" \
  siemForwarder-rt/src/com/acme/siem/BoundedEventQueue.java \
  siemForwarder-rt/src/com/acme/siem/SiemEvent.java \
  tests/src/com/acme/siem/*.java

exec "$JAVA" -cp "$OUT" com.acme.siem.TestMain
