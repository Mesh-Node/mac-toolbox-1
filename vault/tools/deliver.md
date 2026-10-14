---
title: "Tool: deliver"
type: tool
status: draft
evidence: untested
verified_on: "2026-10-12"
secrets: false
---

# deliver

Wait until hermes is on the head tty. Paste the hop packet. Close the tail.

The 80% script starts this and returns. The packet inject is the close.

## Command

```
scripts/mac-deliver.py
```

The pointer is `~/.hermes/hops/deliver.txt`. Three lines: head tty, tail tty, packet path.

## In

Hermes is starting on the head. The packet file is the hop packet.

## Out

`closed /dev/ttysNNN` and exit 0 means the packet was pasted and the tail left the process list.

`hermes did not appear on /dev/ttysNNN` and exit 4 means the wait ended with no hermes on the head. The tail stays open.

## Ran

Awaiting a run.

## Then

The head has the packet. See [[close-the-tty]].
