#!/bin/sh
# Type one line into one Terminal tab and press Return.
# Argument 1 is the tty. Argument 2 is the line.
set -eu
ADDR=${1:-}
TEXT=${2:-}
[ -n "$ADDR" ] && [ -n "$TEXT" ] || { echo "mac-inject.sh takes a tty and a line" >&2; exit 2; }
case "$ADDR" in
  /dev/ttys[0-9]*|ttys[0-9]*) ;;
  *) echo "mac-inject.sh takes one tty address: $ADDR" >&2; exit 2 ;;
esac
case "$(uname -s)" in
  Darwin) ;;
  *) echo "mac-inject.sh runs on Darwin" >&2; exit 5 ;;
esac
SHORT=${ADDR#/dev/}
[ -e "/dev/$SHORT" ] || { echo "tty is /dev/$SHORT" >&2; exit 4; }

# The title token makes this tty one Window menu item. The write is display, not a command.
TOKEN="TYPE-$SHORT"
printf '\033]0;%s\007' "$TOKEN" > "/dev/$SHORT"

osascript - "$TOKEN" "$TEXT" <<'APP'
on run argv
  set token to item 1 of argv
  set commandLine to item 2 of argv
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
      if hits is not 1 then error "Window menu hits for " & token & " is " & hits
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
      delay 0.3
      keystroke commandLine
      keystroke return
      delay 0.3
      keystroke return
    end tell
  end tell
end run
APP

echo "typed on /dev/$SHORT"
exit 0
