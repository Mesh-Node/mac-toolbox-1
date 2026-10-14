---
title: "hop-80"
type: chain
status: draft
evidence: untested
verified_on: "2026-10-12"
secrets: false
tools:
  - "[[hop]]"
  - "[[new-tab]]"
  - "[[inject]]"
  - "[[deliver]]"
  - "[[close-the-tty]]"
---

# hop-80

This is the only toolchain.

When a chat gets too long, the work moves to a fresh tab. The old chat is the tail. The new tab is the head. The old conversation is not copied over.

At 80% of the window, the tail writes a short packet. It names the task, where that task left off, and tells the new session to read the last 3 turns of the tail. If the tail has chosen extra files or artifacts, those are listed too. Nothing else goes in the packet.

The tail opens one new tab, starts Hermes there, and returns. The tail stays open for a moment.

[[deliver]] waits until Hermes is up in the new tab, pastes that packet in, and closes the tail. The paste is what closes the old tab.

The new session starts on that packet. It reads the last 3 turns for the story, and only the files the tail chose.
