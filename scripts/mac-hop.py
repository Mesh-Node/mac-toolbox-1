#!/usr/bin/env python3
"""End of turn. At 80% of this session's window, inject the packet and close.

The open script prints head= and tail=. The harness inject types one line
into the head: hermes chat --cli --query-file <packet>. That line is the
shared start. It does not close. Hop-80 closes the tail after that inject
exits 0. --dry-run prints the job and leaves the current tab open.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

# Toolbox scripts live next to this file.
ROOT = Path(__file__).resolve().parent
# Tail address and the job file are written here. The head reads the job file.
HOPS = Path.home() / ".hermes" / "hops"
# Peak billed prompt size for this session is the highest in= in this log.
LOG = Path.home() / ".hermes" / "logs" / "agent.log"
# Sessions and messages. The accept check reads this file.
DB = Path.home() / ".hermes" / "state.db"
# Advertised context length for grok-4.7, used when the session cache has no row.
CACHE = Path.home() / ".hermes" / "cache" / "endpoint_model_metadata.json"
# Context length the status bar uses: model@billing_base_url.
CTX_CACHE = Path.home() / ".hermes" / "context_length_cache.yaml"
# One billed input count from an agent-log API line.
IN_RE = re.compile(r" in=(\d+) ")
# Open one tab. Prints head= and tail=.
OPEN = ROOT / "mac-new-tab.sh"
# Shared start. Packet file is the first message. Does not close.
HARNESS = ROOT / "mac-inject-harness.sh"
# Close one tty. Hop-80 runs this after the harness inject exits 0.
CLOSE = ROOT / "mac-close-tty.sh"


def _stdin() -> dict:
    """Hook payload. A terminal run with no pipe is an empty payload."""
    raw = "" if sys.stdin.isatty() else sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        data = {}
    return data if isinstance(data, dict) else {}


def _db():
    """Read-only connection to the Hermes session database."""
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def _session_route(session_id: str) -> tuple[str, str]:
    """Model and billing URL stored for this session. Both empty if the row is missing."""
    if not session_id or not DB.is_file():
        return "", ""
    con = _db()
    try:
        row = con.execute(
            "SELECT model, billing_base_url FROM sessions WHERE id=?",
            (session_id,),
        ).fetchone()
    finally:
        con.close()
    if not row:
        return "", ""
    return str(row[0] or "").strip(), str(row[1] or "").strip()


def _cached_window(model: str, base_url: str) -> int:
    """Context length from context_length_cache.yaml. The key is model@url. 0 if absent."""
    if not model or not CTX_CACHE.is_file():
        return 0
    key = f"{model}@{(base_url or '').rstrip('/')}"
    for line in CTX_CACHE.read_text(errors="replace").splitlines():
        text = line.strip()
        if not text.startswith(key + ":"):
            continue
        # A cache key contains colons. The integer is after the last colon.
        try:
            return int(text.rsplit(":", 1)[1].strip())
        except ValueError:
            return 0
    return 0


def _grok_window(model: str) -> int:
    """Advertised grok-4.7 context length. 0 for any other model or a bad cache."""
    if model != "grok-4.7" or not CACHE.is_file():
        return 0
    try:
        models = json.loads(CACHE.read_text()).get("https://api.x.ai/v1", {}).get("models", {})
        return int((models.get("grok-4.7") or {}).get("context_length") or 0)
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0


def _window(session_id: str, payload: dict) -> int:
    """Window for the 80% line. Session cache, then grok cache, then 256000."""
    model = str(payload.get("model") or "").strip()
    base = str(payload.get("base_url") or payload.get("billing_base_url") or "").strip()
    if not model or not base:
        stored_model, stored_base = _session_route(session_id)
        model = model or stored_model
        base = base or stored_base
    cached = _cached_window(model, base)
    if cached > 0:
        return cached
    grok = _grok_window(model)
    if grok > 0:
        return grok
    return 256_000


def _anchor(session_id: str) -> int:
    """Saved prompt-token anchor. It lags an in-flight turn. 0 if unset."""
    if not session_id or not DB.is_file():
        return 0
    con = _db()
    try:
        row = con.execute(
            "SELECT model_config FROM sessions WHERE id=?", (session_id,)
        ).fetchone()
    finally:
        con.close()
    if not row or not row[0]:
        return 0
    try:
        return int((json.loads(row[0]).get("_usage_anchor") or {}).get("prompt_tokens") or 0)
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0


def _billed(session_id: str) -> int:
    """Highest billed in= for this session in the agent log. 0 if the log has no row."""
    if not session_id or not LOG.is_file():
        return 0
    peak = 0
    for line in LOG.read_text(errors="replace").splitlines():
        if session_id not in line or "API call #" not in line:
            continue
        match = IN_RE.search(line)
        if match:
            peak = max(peak, int(match.group(1)))
    return peak


def _one_line(text: str, limit: int = 180) -> str:
    """Collapse whitespace and cap the length. Used for the job and the accept check."""
    return " ".join(str(text).split())[:limit].rstrip()


_PATH_RE = re.compile(r"(?:/Users/\S+|~/[^\s,;]+)")


def _named_file(text: str) -> str:
    """A file the message already names. Empty when none exists."""
    for raw in _PATH_RE.findall(text):
        path = Path(raw.rstrip(".,)")).expanduser()
        if path.is_file():
            return str(path)
    return ""


def _task(text: str) -> str:
    """One task sentence. A hop prefix is unwrapped. An old packet is empty."""
    line = _one_line(text, limit=240)
    if line.startswith("kind: hop"):
        return ""
    if line.startswith("The job is:"):
        line = line[len("The job is:") :].strip()
        line = line.split(". ", 1)[0].rstrip(".").strip()
    return line


_FILE_TOOLS = {"read_file", "write_file", "patch"}


def _job(session_id: str) -> str:
    """Latest user line. Short lines count. A one-word reply walks back."""
    if not session_id or not DB.is_file():
        return ""
    con = _db()
    try:
        rows = con.execute(
            "SELECT content FROM messages WHERE session_id=? AND role='user' "
            "ORDER BY id DESC LIMIT 8",
            (session_id,),
        ).fetchall()
    finally:
        con.close()
    for (content,) in rows:
        line = _task(content)
        if len(line) >= 12:
            return line
    return ""


def _continue_line(text: str) -> str:
    """First sentence of the reply that just finished."""
    line = _one_line(text, limit=180)
    if not line:
        return ""
    return line.split(". ", 1)[0].rstrip(".").strip()


def _call_path(call: object) -> str:
    """A file a read, write, or patch call opened. Empty otherwise."""
    if not isinstance(call, dict):
        return ""
    function = call.get("function")
    fn = function if isinstance(function, dict) else call
    if not isinstance(fn, dict):
        return ""
    name = str(fn.get("name") or "")
    if name not in _FILE_TOOLS:
        return ""
    args = fn.get("arguments") if isinstance(fn, dict) else None
    if args is None:
        args = call.get("arguments")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            return ""
    if not isinstance(args, dict):
        return ""
    raw = str(args.get("path") or "")
    path = Path(raw).expanduser() if raw else None
    if path is not None and path.is_file():
        return str(path)
    return ""


def _iter_calls(message: dict) -> list:
    """Tool calls on one message. A JSON string is decoded."""
    calls = message.get("tool_calls") or []
    if isinstance(calls, str):
        try:
            calls = json.loads(calls)
        except json.JSONDecodeError:
            return []
    return calls if isinstance(calls, list) else []


def _files_from_turn(messages: list, task_text: str) -> list[str]:
    """Files the crossing turn opened, plus a file the task already names. Cap 5."""
    start = 0
    for index, message in enumerate(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            start = index + 1
    found: list[str] = []
    named = _named_file(task_text)
    if named:
        found.append(named)
    for message in messages[start:]:
        if not isinstance(message, dict):
            continue
        for call in _iter_calls(message):
            path = _call_path(call)
            if path and path not in found:
                found.append(path)
            if len(found) >= 5:
                return found
    return found


def _db_packet_parts(session_id: str) -> tuple[str, list[str], str]:
    """Continue line, files, and the user text of the task turn. From the session rows."""
    if not session_id or not DB.is_file():
        return "", [], ""
    con = _db()
    try:
        rows = con.execute(
            "SELECT role, content, tool_calls FROM messages WHERE session_id=? ORDER BY id",
            (session_id,),
        ).fetchall()
    finally:
        con.close()
    messages = [
        {"role": role, "content": content or "", "tool_calls": calls}
        for role, content, calls in rows
    ]
    cont = ""
    user_text = ""
    for message in reversed(messages):
        if message["role"] == "assistant" and str(message["content"]).strip() and not cont:
            cont = _continue_line(message["content"])
        if message["role"] == "user" and not user_text:
            user_text = str(message["content"])
        if cont and user_text:
            break
    return cont, _files_from_turn(messages, user_text), user_text


def _packet(session_id: str, payload: dict) -> str:
    """The query file. Task, continue line, conversation pointer, files that turn opened."""
    raw_extra = payload.get("extra")
    extra = raw_extra if isinstance(raw_extra, dict) else {}
    profile = str(payload.get("profile") or "default").strip() or "default"
    user_text = extra.get("user_message")
    task = _task(user_text) if isinstance(user_text, str) else ""
    if len(task) < 12:
        task = _job(session_id)
    if len(task) < 12 or not session_id:
        return ""
    reply = extra.get("assistant_response")
    cont = _continue_line(reply) if isinstance(reply, str) else ""
    if not cont:
        db_cont, _db_files, _db_user = _db_packet_parts(session_id)
        cont = db_cont
    files = _chosen_files(session_id)
    lines = [f"Task: {task}"]
    if cont:
        lines.append(f"Continue: {cont}")
    lines.append(f"Read the last 3 turns of @session:{profile}/{session_id}.")
    if files:
        lines.append("Read:")
        lines.extend(files)
    return "\n".join(lines)


def _chosen_files(session_id: str) -> list[str]:
    """Paths the tail named for the new session. Empty when the tail named none."""
    named = HOPS / f"context-{session_id}.txt"
    if not named.is_file():
        return []
    found: list[str] = []
    for raw in named.read_text().splitlines():
        text = raw.strip()
        if not text:
            continue
        path = Path(text).expanduser()
        if path.exists() and str(path) not in found:
            found.append(str(path))
        if len(found) >= 5:
            break
    return found


def _assignments(text: str) -> dict[str, str]:
    """head= and tail= from mac-new-tab.sh. new= and donor= are the old names."""
    found = {}
    for line in text.splitlines():
        if line.startswith("head=") or line.startswith("tail=") or line.startswith("new=") or line.startswith("donor="):
            key, _, value = line.partition("=")
            found[key] = value.strip()
    return found


def _run(argv: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run one toolbox script. stdout and stderr come back in the result."""
    return subprocess.run(argv, text=True, capture_output=True, timeout=timeout)


def main() -> int:
    """80% gate, then hop-80. Close is the last command."""
    dry = "--dry-run" in sys.argv[1:]
    payload = _stdin()
    # The hook sends the session id on stdin. --session is the manual address.
    session_id = str(
        payload.get("session_id") or os.environ.get("HERMES_SESSION_ID") or ""
    ).strip()
    if "--session" in sys.argv:
        session_id = sys.argv[sys.argv.index("--session") + 1]
    # The line is 80% of this session's window, as an integer.
    window = _window(session_id, payload)
    line = int(window * 0.8)
    # The higher of the saved anchor and the billed log peak.
    used = max(_anchor(session_id), _billed(session_id))
    # Under the line the turn continues. No tab opens.
    if used < line:
        return 0
    # One fire per session. A second turn at the line does not open a second tab.
    latch = HOPS / f"fired-{session_id or 'unknown'}"
    if latch.exists() and not dry:
        return 0
    job = _packet(session_id, payload)
    if not job:
        print("awaiting a live task", file=sys.stderr)
        return 0
    # Dry-run prints the job and stops. The current tab stays open.
    if dry:
        print(f"{used}/{line} window {window}")
        print(job)
        print("dry-run — current tab stays open", file=sys.stderr)
        return 0
    # Step 1 and 2. Open the head tab. The open script prints head= and tail=.
    opened = _run([str(OPEN)], timeout=20)
    if opened.returncode != 0:
        sys.stderr.write(opened.stderr or opened.stdout)
        return opened.returncode or 4
    names = _assignments(opened.stdout)
    head = names.get("head") or names.get("new", "")
    tail = names.get("tail") or names.get("donor", "")
    if not head or not tail:
        print("open did not print head and tail", file=sys.stderr)
        return 4
    # Tail address for a later mesh action. It is not written into the job.
    HOPS.mkdir(parents=True, exist_ok=True)
    (HOPS / "tail").write_text(tail + "\n")
    os.chmod(HOPS / "tail", 0o600)
    # Step 3. The query file is the job only.
    query = HOPS / f"job-{session_id or 'unknown'}.txt"
    query.write_text(job + "\n")
    os.chmod(query, 0o600)
    # Shared start. One line into the head. The packet file is the first message.
    # A miss leaves the tail open and writes no latch, so the next turn can retry.
    started = _run([str(HARNESS), head, str(query)], timeout=30)
    if started.returncode != 0:
        sys.stderr.write(started.stderr or started.stdout)
        print(opened.stdout.strip())
        return started.returncode or 4
    # The latch is on disk before the close. Closing this tty can stop this process.
    latch.write_text(f"{used}/{line}\n")
    os.chmod(latch, 0o600)
    with latch.open("rb") as handle:
        os.fsync(handle.fileno())
    # Hop-80 addition. Close the tail only after the inject exited 0.
    # A new session so Command-W does not kill the close before it finishes.
    closing = subprocess.Popen(
        [str(CLOSE), tail],
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        closed_out, _ = closing.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        closing.kill()
        print(opened.stdout.strip())
        sys.stdout.write(started.stdout)
        print("close timed out", file=sys.stderr)
        return 4
    print(opened.stdout.strip())
    sys.stdout.write(started.stdout)
    if closed_out:
        sys.stdout.write(closed_out if closed_out.endswith("\n") else closed_out + "\n")
    return closing.returncode or 0


if __name__ == "__main__":
    raise SystemExit(main())
