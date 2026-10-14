---
title: "Tool: flag the tail"
type: tool
status: draft
evidence: untested
verified_on: "2026-10-14"
secrets: false
---

# flag the tail

On chat completion, type one flag into the tail tty.

The hook is `hooks.post_llm_call`. It runs once per turn after the tool loop. It does not call the model. It does not close a tty.

The wait file is `~/.hermes/hops/flag-wait`. Two lines: `tail=` and `packet=`. [[open-harness]] writes it. A completion whose user message is that packet types `flag: head complete` into the tail, writes `flag-sent`, and removes the wait file. Any other completion exits 0.

## Command

The completion hook already registered is `~/.hermes/hops/on-complete.py`. It execs this script.

## Ran

2026-10-14, this Mac. Head session 20261014_084632_c78792 finished its turn. The hook typed `flag: head complete` into /dev/ttys012. flag-wait was removed. flag-sent names that tail and that session. Both ttys stayed open.

`typed on /dev/ttysNNN` when the flag landed.

No output and exit 0 when no wait file is present, or the user message is not the packet.

Inject's refusal passes through. The wait file stays, so a later completion of that same packet can retry. A retry needs the same user message, so the first completion is the send.
