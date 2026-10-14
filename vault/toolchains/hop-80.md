---
title: "hop-80"
type: chain
status: draft
evidence: verified-local
verified_on: "2026-10-14"
secrets: false
tools:
  - "[[hop]]"
  - "[[new-tab]]"
  - "[[inject-harness]]"
  - "[[inject]]"
  - "[[close-the-tty]]"
---

# hop-80

This is the 80% toolchain.

When a chat gets too long, the work moves to a fresh tab. The old chat is the tail. The new tab is the head. The old conversation is not copied over.

The shared start is [[inject-harness]]. It types one line into the head. That line starts Hermes with the packet file as the first message. Other workflows stop there. The tail stays open.

Hop-80 adds one step after that line has landed. [[close-the-tty]] closes the tail. A miss from inject leaves the tail open and writes no latch.

At 80% of the window, the tail writes a short packet. It names the task, where that task left off, and tells the new session to read the last 3 turns of the tail. If the tail has chosen extra files, those are listed too. Nothing else goes in the packet.

The new session starts on that packet. It reads the last 3 turns for the story, and only the files the tail chose.

14 October 2026, this Mac. The head log seeded a 290-character query file. The hook printed `typed on`, then `closed`. The first message was the packet.
