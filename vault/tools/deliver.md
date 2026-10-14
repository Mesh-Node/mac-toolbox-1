---
title: "Tool: deliver"
type: tool
status: draft
evidence: untested
verified_on: "2026-10-12"
secrets: false
---

# deliver

Not the hop-80 close. The live chain injects one line with [[inject-harness]], then [[close-the-tty]] closes the tail after that inject exits 0.

This file pastes with Command-V even when the Window menu has no matching tab, and it treats a hermes process row as ready. That paste is not a landed packet. Awaiting a rewrite before any workflow calls it.

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
