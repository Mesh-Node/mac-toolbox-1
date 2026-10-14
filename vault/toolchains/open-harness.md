---
title: "open-harness"
type: chain
status: draft
evidence: verified-local
verified_on: "2026-10-14"
secrets: false
---

# open-harness

The testable base. No 80% gate. No tail close.

[[new-tab]] prints head= and tail=. [[inject-harness]] types one line into the head. That line starts Hermes with the packet file as the first message. The tail stays open.

The completion hook is [[flag-tail]]. It runs on post_llm_call, once per turn, after the tool loop. It does not call the model. When the user message is the packet, it types `flag: head complete` into the tail tty and clears the wait file.

[[hop-80]] is this chain plus the 80% gate and the tail close.
