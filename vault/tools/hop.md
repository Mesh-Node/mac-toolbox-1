---
title: "Tool: hop"
type: tool
status: draft
evidence: verified-local
verified_on: "2026-10-12"
secrets: false
---

# hop

End of turn. When this session's peak prompt is at or over 80% of its window, open one tab and send the current job there.

The file is Python. The installed hook execs it. Under the line it exits 0 and prints nothing. Over the line it runs [[new-tab]], then [[inject]] with `hermes chat --cli`, then [[inject]] with the job line.

The job line is the latest user line of the session that crossed. The donor tty is the `donor=` line from the open. The packet is one sentence of job, that donor tab, and the close of that tab.

## Command

```
scripts/mac-hop.py
scripts/mac-hop.py --dry-run --session <id>
```

The hook passes the session id on stdin. `--dry-run` prints the line and leaves the current tab open.

## In

Session id from the hook. Prompt size from the saved anchor and the highest `in=` in the agent log. Window from the endpoint cache for grok-4.7, else the context-length cache, else 256000.

## Out

Under the line: no output, exit 0.

A dry-run over the line prints `used/line window N`, the job sentence, and `dry-run — current tab stays open` on stderr. Exit 0.

A live run over the line prints the open script's `new=` and `donor=` lines, then `typed on /dev/ttysNNN`. One latch per session, so the next turn does not open a second tab.

## Ran

2026-10-12, this Mac. `--dry-run --session 20261011_204136_6705f3` printed `410558/400000 window 500000` and the job sentence from that session. The current tab stayed open. A live run of the same session exited 0 because a latch file was already present. That latch is there so this turn does not open a tab and name this tty as the donor to close.

## Then

The new tab reads the job sentence. The close of `"$donor"` is the line in that sentence.
