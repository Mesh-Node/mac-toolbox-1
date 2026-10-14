---
title: "Tool: hop"
type: tool
status: draft
evidence: verified-local
verified_on: "2026-10-12"
secrets: false
---

# hop

End of turn. When this session's prompt is at or over 80% of its window, the tail builds the hop packet, opens a tab, types `hermes` and Return, and returns. The old window is not copied.

Two tty numbers:

- tail: the tty of the session that built the packet. Later messages and actions use this tty. Close is one of those actions.
- head: the tty of the new tab. The packet goes there.

The two numbers are different.

The file is Python. The installed hook execs it. Under the line it exits 0 and prints nothing. Over the line it opens one tab, types `hermes` and Return, and returns. [[deliver]] pastes the packet and closes the tail.

The packet is only these lines. `Task:` is the latest user line of the session that crossed, including a short line. A line that starts with `The job is:` is unwrapped to its first sentence. A line that starts with `kind: hop` is skipped. `Continue:` is the first sentence of the reply that just finished. The next line is `Read the last 3 turns of @session:<profile>/<id>.` `Read:` lists the paths the tail wrote in `~/.hermes/hops/context-<session id>.txt`, at most five, and only paths that exist. The tail address is not in the packet.

## Command

```
scripts/mac-hop.py
scripts/mac-hop.py --dry-run --session <id>
```

The hook passes the session id on stdin. `--dry-run` prints the job and leaves the current tab open.

## In

Session id from the hook. Prompt size from the saved anchor and the highest `in=` in the agent log. Window from the context-length cache for this session's model, else the grok endpoint cache, else 256000.

## Out

Under the line: no output, exit 0.

A dry-run over the line prints `used/line window N`, the job, and `dry-run — current tab stays open` on stderr. Exit 0.

A live run over the line prints `head=` and `tail=`, then `hermes started on /dev/ttysNNN`, and returns. The tail stays open. [[deliver]] pastes the packet and prints `closed /dev/ttysNNN`.

## Ran

2026-10-12, this Mac. `--dry-run --session 20261011_204136_6705f3` printed `410558/400000 window 500000` and the job sentence from that session. The current tab stayed open. A live run of the same session exited 0 because a latch file was already present. That latch keeps this turn from opening a second tab.

2026-10-12, this Mac. `--dry-run --session 20261012_125328_560150` printed `401740/400000 window 500000` and a job whose first line is `Task: how often is this folder cleaned?` The job also has `Continue:`, `Read the last turn of @session:default/20261012_125328_560150.`, and two `Read:` files. The current tab stayed open. Exit 0.

## Then

[[deliver]] pastes the packet and closes the tail.
