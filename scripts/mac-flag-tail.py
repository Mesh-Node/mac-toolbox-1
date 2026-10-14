#!/usr/bin/env python3
"""On chat completion, send one flag to the tail recorded in flag-wait.

No model call. No 80% gate. No tty close.

This hook runs at the end of every Hermes turn that loaded it. Most turns
are not the head. Those turns must exit 0 and type nothing.

Every return 0 before the inject is the same outcome: do not flag.
A real miss looks the same as "not our turn." The wait file stays.
The only loud failure is the inject itself.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOPS = Path.home() / ".hermes" / "hops"
WAIT = HOPS / "flag-wait"
SENT = HOPS / "flag-sent"
# Inject sits next to this file. A clone uses that path.
INJECT = Path(__file__).resolve().parent / "mac-inject.sh"
FLAG = "flag: head complete"


def _fields(text: str) -> dict[str, str]:
    """Read tail= and packet= lines. A line without '=' is skipped."""
    found: dict[str, str] = {}
    for line in text.splitlines():
        key, sep, value = line.partition("=")
        if sep:
            found[key.strip()] = value.strip()
    return found


def _same(left: str, right: str) -> bool:
    """Compare the turn text to the packet file. Whitespace does not count."""
    return " ".join(left.split()) == " ".join(right.split())


def main() -> int:
    # No head is in flight. This is the common case. Stay quiet.
    if not WAIT.is_file():
        return 0

    # The hook writes JSON on stdin. A hand run in a terminal has no pipe.
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        # Broken JSON. Do not flag. Also do not say why. Wait file stays.
        return 0
    if not isinstance(payload, dict):
        return 0

    # The shell hook puts user_message under extra, not at the top.
    # A payload that moves that field will miss here and exit 0.
    extra = payload.get("extra")
    if not isinstance(extra, dict):
        return 0
    user = extra.get("user_message")
    if not isinstance(user, str):
        return 0

    fields = _fields(WAIT.read_text())
    tail = fields.get("tail", "")
    packet = fields.get("packet", "")
    # A wait file with a missing line, or a packet that was deleted.
    # Same silent exit as "not our turn."
    if not tail or not packet or not Path(packet).is_file():
        return 0

    # Other sessions, and later turns of the head, land here.
    # The match is the whole packet text. A wrapped message does not match.
    if not _same(user, Path(packet).read_text()):
        return 0

    # This turn is the head's packet. Type the flag into the tail tty.
    typed = subprocess.run(
        [str(INJECT), tail, FLAG], text=True, capture_output=True
    )
    if typed.returncode != 0:
        # Inject refused. Leave the wait file. A later turn will not match
        # unless its user message is the same packet text, so this is not a retry.
        sys.stderr.write(typed.stderr or typed.stdout)
        return typed.returncode or 4

    # Record the send, then remove the wait file so the next turn does not flag again.
    SENT.write_text(
        f"tail={tail}\nsession={payload.get('session_id', '')}\n{FLAG}\n"
    )
    SENT.chmod(0o600)
    WAIT.unlink(missing_ok=True)
    sys.stdout.write(typed.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
