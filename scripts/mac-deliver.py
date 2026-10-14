#!/usr/bin/env python3
"""Wait until hermes is on the head tty, paste the packet, close the tail.

The 80% script starts this and returns. The packet inject is the close.
The packet is pasted as written, then one Return submits it.
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

HOPS = Path.home() / ".hermes" / "hops"
ROOT = Path(__file__).resolve().parent
CLOSE = ROOT / "mac-close-tty.sh"
POINTER = HOPS / "deliver.txt"


def _hermes_on(tty: str) -> bool:
    short = tty.removeprefix("/dev/")
    done = subprocess.run(
        ["ps", "-t", short, "-o", "command="],
        text=True,
        capture_output=True,
    )
    return "hermes" in done.stdout


def _paste(tty: str) -> subprocess.CompletedProcess[str]:
    short = tty.removeprefix("/dev/")
    token = f"TYPE-{short}"
    subprocess.run(
        ["bash", "-c", f"printf '\\033]0;{token}\\007' > /dev/{short}"],
        check=False,
    )
    script = """
on run argv
  set token to item 1 of argv
  tell application "System Events"
    tell process "Terminal"
      set frontmost to true
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
      keystroke "v" using command down
      keystroke return
    end tell
  end tell
end run
"""
    return subprocess.run(
        ["osascript", "-e", script, token],
        text=True,
        capture_output=True,
    )


def main() -> int:
    if not POINTER.is_file():
        return 0
    lines = POINTER.read_text().splitlines()
    if len(lines) < 3:
        return 4
    head, tail, packet = lines[0].strip(), lines[1].strip(), lines[2].strip()
    job = Path(packet).read_text().strip() + "\n"
    for _ in range(40):
        if _hermes_on(head):
            break
        time.sleep(0.25)
    else:
        print(f"hermes did not appear on {head}", flush=True)
        return 4
    copied = subprocess.run(["pbcopy"], input=job, text=True)
    if copied.returncode != 0:
        return copied.returncode or 4
    pasted = _paste(head)
    if pasted.returncode != 0:
        print(pasted.stderr or pasted.stdout, end="", flush=True)
        return pasted.returncode or 4
    closed = subprocess.run([str(CLOSE), tail], text=True, capture_output=True)
    print((closed.stdout or closed.stderr).strip(), flush=True)
    POINTER.unlink(missing_ok=True)
    return closed.returncode or 0


if __name__ == "__main__":
    raise SystemExit(main())
