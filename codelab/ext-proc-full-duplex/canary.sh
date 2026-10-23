#!/bin/sh
# A control that exercises the body: send random bytes through the proxy, compare what comes back.
set -eu
URL="${1:-http://localhost:10000/echo}"
head -c 300000 /dev/urandom > /tmp/canary.in
curl -s "$URL" --data-binary @/tmp/canary.in -o /tmp/canary.out
sent=$(shasum -a 256 < /tmp/canary.in | cut -c1-16)
got=$(shasum -a 256 < /tmp/canary.out | cut -c1-16)
if [ "$sent" = "$got" ]; then
  echo "canary OK: 300000 bytes round-tripped ($sent)"
else
  echo "canary FAILED: sent $sent, got $got ($(wc -c < /tmp/canary.out | tr -d ' ') bytes back)"
  exit 1
fi
