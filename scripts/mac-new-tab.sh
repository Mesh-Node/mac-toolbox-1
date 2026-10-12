#!/bin/sh
# Open one Terminal tab and print the new tty and the donor tty.
# The chain stores those two lines. Later tools receive them as arguments.
set -eu
case "$(uname -s)" in
  Darwin) ;;
  *) echo "mac-new-tab.sh runs on Darwin" >&2; exit 5 ;;
esac

# The tty of this process when this process sits in a Terminal tab.
donor_tty() {
  pid=$$
  i=0
  while [ "$pid" != 1 ] && [ "$i" -lt 16 ]; do
    t=$(ps -o tty= -p "$pid" 2>/dev/null | tr -d ' ')
    case "$t" in
      ttys[0-9]*) printf '%s\n' "$t"; return 0 ;;
    esac
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
    [ -n "$pid" ] || break
    i=$((i + 1))
  done
  return 1
}

# Every tty whose ancestor is Terminal.app.
terminal_ttys() {
  ps -axo pid=,ppid=,tty=,command= | awk '
    index($0, "Terminal.app/Contents/MacOS/Terminal") { term[$1] = 1 }
    { parent[$1] = $2; if ($3 ~ /^ttys/) ttyof[$1] = $3 }
    END {
      for (p in ttyof) {
        q = p
        seen = 0
        while (q != 0 && q != 1 && seen < 24) {
          if (q in term) { print ttyof[p]; break }
          q = parent[q]
          seen++
        }
      }
    }
  ' | sort -u
}

DONOR=$(donor_tty) || { echo "donor tty was not found" >&2; exit 4; }
BEFORE=$(terminal_ttys)

# Bring Terminal to the front, then send Command-T.
osascript <<'APP'
tell application "System Events"
  tell process "Terminal"
    set frontmost to true
    keystroke "t" using command down
  end tell
end tell
APP

# The new tty is the Terminal tty that was not in the list before Command-T.
before_f=$(mktemp)
now_f=$(mktemp)
trap 'rm -f "$before_f" "$now_f"' EXIT
printf '%s\n' "$BEFORE" | sort -u > "$before_f"
NEW=""
i=0
while [ "$i" -lt 20 ]; do
  NOW=$(terminal_ttys)
  printf '%s\n' "$NOW" | sort -u > "$now_f"
  NEW=$(comm -13 "$before_f" "$now_f" | head -n 1)
  COUNT=$(comm -13 "$before_f" "$now_f" | awk 'NF{c++} END{print c+0}')
  if [ "$COUNT" -eq 1 ] && [ -n "$NEW" ]; then
    break
  fi
  NEW=""
  i=$((i + 1))
  sleep 0.25
done

[ -n "$NEW" ] || { echo "new tty was not found" >&2; exit 4; }

printf 'new=/dev/%s\n' "$NEW"
printf 'donor=/dev/%s\n' "$DONOR"
exit 0
