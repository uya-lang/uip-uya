#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/ubuntu/Documents/uip-uya"
APP="/tmp/uya_uip_unix"

cd "$ROOT"

echo '[1/4] prepare tap0'
make -C examples/unix tap-up

echo '[2/4] build app'
make -C examples/unix build

echo '[3/4] start app'
pkill -f "$APP" 2>/dev/null || true
"$APP" >/tmp/uya_uip_unix.log 2>&1 &
APP_PID=$!
trap 'kill $APP_PID 2>/dev/null || true' EXIT
sleep 1

echo '[4/4] verify hello response'
if command -v nc >/dev/null 2>&1; then
  RESPONSE="$(printf '' | nc -w 2 192.168.0.2 1234 || true)"
  echo "response: $RESPONSE"
  if [[ "$RESPONSE" == *"helloworld"* ]]; then
    echo 'OK: hello service responded'
    exit 0
  fi
  echo 'FAIL: hello service did not respond as expected'
  exit 1
else
  echo 'nc not found; app started, but response check skipped'
fi
