#!/usr/bin/env python3
"""End of turn. At 80% of this session's window, open a tab and send the job.

The open script prints new= and donor=. Inject types into the new tty.
The packet names the current job and the donor tab to close.
--dry-run prints the packet and leaves the current tab open.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOPS = Path.home() / ".hermes" / "hops"
LOG = Path.home() / ".hermes" / "logs" / "agent.log"
DB = Path.home() / ".hermes" / "state.db"
CACHE = Path.home() / ".hermes" / "cache" / "endpoint_model_metadata.json"
CTX_CACHE = Path.home() / ".hermes" / "context_length_cache.yaml"
IN_RE = re.compile(r" in=(\d+) ")
OPEN = ROOT / "mac-new-tab.sh"
INJECT = ROOT / "mac-inject.sh"


def _stdin() -> dict:
    raw = "" if sys.stdin.isatty() else sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        data = {}
    return data if isinstance(data, dict) else {}


def _db():
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def _session_route(session_id: str) -> tuple[str, str]:
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
    if not model or not CTX_CACHE.is_file():
        return 0
    key = f"{model}@{(base_url or '').rstrip('/')}"
    for line in CTX_CACHE.read_text(errors="replace").splitlines():
        text = line.strip()
        if not text.startswith(key + ":"):
            continue
        try:
            return int(text.rsplit(":", 1)[1].strip())
        except ValueError:
            return 0
    return 0


def _grok_window(model: str) -> int:
    if model != "grok-4.7" or not CACHE.is_file():
        return 0
    try:
        models = json.loads(CACHE.read_text()).get("https://api.x.ai/v1", {}).get("models", {})
        return int((models.get("grok-4.7") or {}).get("context_length") or 0)
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0


def _window(session_id: str, payload: dict) -> int:
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
    return " ".join(str(text).split())[:limit].rstrip()


def _job(session_id: str) -> str:
    if not session_id or not DB.is_file():
        return ""
    con = _db()
    try:
        rows = con.execute(
            "SELECT content FROM messages WHERE session_id=? AND role='user' "
            "AND length(content)>=40 ORDER BY id DESC LIMIT 8",
            (session_id,),
        ).fetchall()
    finally:
        con.close()
    for (content,) in rows:
        line = _one_line(content)
        if line and not line.startswith("The job is:") and not line.startswith("kind: hop"):
            return line
    return ""


def _assignments(text: str) -> dict[str, str]:
    found = {}
    for line in text.splitlines():
        if line.startswith("new=") or line.startswith("donor="):
            key, _, value = line.partition("=")
            found[key] = value.strip()
    return found


def _run(argv: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, text=True, capture_output=True, timeout=timeout)


def _hermes_on(tty: str) -> bool:
    short = tty.removeprefix("/dev/")
    done = _run(["ps", "-axo", "tty=,command="], timeout=10)
    for line in done.stdout.splitlines():
        if line.split(None, 1)[:1] == [short] and "hermes-agent" in line:
            return True
    return False


def main() -> int:
    dry = "--dry-run" in sys.argv[1:]
    payload = _stdin()
    session_id = str(
        payload.get("session_id") or os.environ.get("HERMES_SESSION_ID") or ""
    ).strip()
    if "--session" in sys.argv:
        session_id = sys.argv[sys.argv.index("--session") + 1]
    window = _window(session_id, payload)
    line = int(window * 0.8)
    used = max(_anchor(session_id), _billed(session_id))
    if used < line:
        return 0
    latch = HOPS / f"fired-{session_id or 'unknown'}"
    if latch.exists() and not dry:
        return 0
    job = _job(session_id)
    if not job:
        print("awaiting a live task", file=sys.stderr)
        return 0
    if dry:
        print(f"{used}/{line} window {window}")
        print(f"The job is: {job.rstrip('.')}. Continue that job from the donor tab. Close the donor tab.")
        print("dry-run — current tab stays open", file=sys.stderr)
        return 0
    opened = _run([str(OPEN)], timeout=20)
    if opened.returncode != 0:
        sys.stderr.write(opened.stderr or opened.stdout)
        return opened.returncode or 4
    names = _assignments(opened.stdout)
    new = names.get("new", "")
    donor = names.get("donor", "")
    if not new or not donor:
        print("open did not print new and donor", file=sys.stderr)
        return 4
    started = _run([str(INJECT), new, "hermes chat --cli"], timeout=20)
    if started.returncode != 0:
        sys.stderr.write(started.stderr or started.stdout)
        return started.returncode or 4
    for _ in range(40):
        if _hermes_on(new):
            break
        subprocess.run(["sleep", "0.25"], check=False)
    else:
        print(f"hermes is not on {new}", file=sys.stderr)
        return 4
    sentence = job[:-1] if job.endswith(".") else job
    packet = (
        f"The job is: {sentence}. "
        f"Continue that job from the donor tab {donor}. "
        f"Close {donor}."
    )
    sent = _run([str(INJECT), new, packet], timeout=20)
    if sent.returncode != 0:
        sys.stderr.write(sent.stderr or sent.stdout)
        return sent.returncode or 4
    HOPS.mkdir(parents=True, exist_ok=True)
    latch.write_text(f"{used}/{line}\n")
    os.chmod(latch, 0o600)
    print(opened.stdout.strip())
    print(sent.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
