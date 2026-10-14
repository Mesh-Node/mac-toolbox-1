#!/bin/sh
# Open one tab and inject a packet into a new Hermes harness.
# No 80% gate. No tail close. The completion hook reads flag-wait and
# sends the flag to the tail tty recorded here.
set -eu
PACKET=${1:-}
# Missing path, or the file is not there. Refuse before a tab opens.
[ -n "$PACKET" ] && [ -f "$PACKET" ] || {
  echo "mac-open-harness.sh takes a packet path" >&2
  exit 2
}
case "$PACKET" in
  /*) ;;
  *) PACKET=$(CDPATH= cd -- "$(dirname "$PACKET")" && pwd)/$(basename "$PACKET") ;;
esac
case "$PACKET" in
  *[[:space:]]*)
    echo "packet path has a space: $PACKET" >&2
    exit 2
    ;;
esac
ROOT=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
HOPS="${HERMES_HOPS:-$HOME/.hermes/hops}"
mkdir -p "$HOPS"
umask 077
# new-tab prints head= and tail=. eval stores those names in this shell.
eval "$("$ROOT/mac-new-tab.sh")"
# Open refused, or the print used other names. Do not write a wait file.
[ -n "${head:-}" ] && [ -n "${tail:-}" ] || {
  echo "open did not print head and tail" >&2
  exit 4
}
WAIT="$HOPS/flag-wait"
printf 'tail=%s\npacket=%s\n' "$tail" "$PACKET" > "$WAIT"
chmod 600 "$WAIT"
# Write the wait file before the inject. The hook reads it when the head finishes.
# If the inject misses, remove the wait file. A later unrelated turn must not flag.
if ! "$ROOT/mac-inject-harness.sh" "$head" "$PACKET"; then
  rm -f "$WAIT"
  printf 'head=%s\n' "$head"
  printf 'tail=%s\n' "$tail"
  echo "inject missed — tail stays open" >&2
  exit 4
fi
printf 'head=%s\n' "$head"
printf 'tail=%s\n' "$tail"
