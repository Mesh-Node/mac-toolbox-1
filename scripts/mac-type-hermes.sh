#!/bin/sh
# Type hermes and Return into the tty argument.
# The address is the new= line from mac-new-tab.sh.
set -eu
ADDR=${1:-}
[ -n "$ADDR" ] || { echo "mac-type-hermes.sh takes one tty address" >&2; exit 2; }
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
exec "$ROOT/mac-inject.sh" "$ADDR" hermes
