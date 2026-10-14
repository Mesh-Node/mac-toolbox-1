#!/bin/sh
# Close one Terminal tab by tty. Quit stays off. Close that one address.
# The Window menu lists the tab. Mark the tty there, click that one item, then Close Tab.
# The Homebrew profile closes the tab on Command-W.
set -eu
ADDR=${1:-}
[ -n "$ADDR" ] || { echo "usage: mac-close-tty.sh /dev/ttysNNN" >&2; exit 2; }
case "$ADDR" in
  /dev/ttys[0-9]*|ttys[0-9]*) ;;
  *)
    echo "refuse: not one tty address: $ADDR" >&2
    exit 2
    ;;
esac
case "$(uname -s)" in
  Darwin) ;;
  *) echo "refuse: mac-close-tty.sh is Darwin only" >&2; exit 5 ;;
esac
SHORT=$ADDR
SHORT=${SHORT#/dev/}
[ -e "/dev/$SHORT" ] || { echo "refuse: no such tty: /dev/$SHORT" >&2; exit 4; }
TOKEN="HOPCLOSE-$SHORT"
printf '\033]0;%s\007' "$TOKEN" > "/dev/$SHORT"
osascript - "$TOKEN" >/dev/null <<'APP'
on run argv
  set token to item 1 of argv
  tell application "System Events"
    tell process "Terminal"
      set frontmost to true
      set hits to 0
      set tries to 0
      repeat while tries < 8
        set hits to 0
        tell menu "Window" of menu bar 1
          repeat with mi in menu items
            set n to name of mi
            if n is missing value then set n to ""
            if n contains token then set hits to hits + 1
          end repeat
        end tell
        if hits is 1 then exit repeat
        set tries to tries + 1
        delay 0.25
      end repeat
      if hits is 0 then error "no tab for " & token
      if hits > 1 then error "refusing: more than one tab matched " & token
      tell menu "Window" of menu bar 1
        repeat with mi in menu items
          set n to name of mi
          if n is missing value then set n to ""
          if n contains token then
            click mi
            exit repeat
          end if
        end repeat
      end tell
      delay 0.2
      keystroke "w" using command down
    end tell
  end tell
end run
APP
i=0
while [ "$i" -lt 12 ]; do
  if ! ps -axo tty= | awk -v t="$SHORT" '$1==t {found=1} END{exit found?0:1}'; then
    echo "closed $ADDR"
    exit 0
  fi
  i=$((i + 1))
  sleep 0.25
done
echo "refuse: $ADDR still open" >&2
exit 4
