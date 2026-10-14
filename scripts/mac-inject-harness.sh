#!/bin/sh
# Start one Hermes harness on one tty. The packet file is its first message.
# Does not close a tty. Hop-80 closes the tail after this exits 0.
set -eu
ADDR=${1:-}
PACKET=${2:-}
[ -n "$ADDR" ] && [ -n "$PACKET" ] || {
  echo "mac-inject-harness.sh takes a tty and a packet path" >&2
  exit 2
}
[ -f "$PACKET" ] || { echo "packet is $PACKET" >&2; exit 2; }
# A space in the path would be typed as more than one shell word.
case "$PACKET" in
  *[[:space:]]*)
    echo "packet path has a space: $PACKET" >&2
    exit 2
    ;;
esac
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
exec "$ROOT/mac-inject.sh" "$ADDR" "hermes chat --cli --query-file $PACKET"
