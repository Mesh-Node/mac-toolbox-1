---
title: "Tool: inject harness"
type: tool
status: draft
evidence: untested
verified_on: "2026-10-14"
secrets: false
---

# inject harness

Start one Hermes harness on one tty. The packet file is its first message. This does not close a tty.

The file is POSIX shell. It calls [[inject]] with one line:

```
hermes chat --cli --query-file <packet>
```

A chat is that line. The single word `hermes` is not a chat. Other workflows call this script and stop. [[hop-80]] calls it, then closes the tail.

## Command

```
scripts/mac-inject-harness.sh /dev/ttysNNN /path/to/packet.txt
```

## In

The tty is `"$head"` from [[new-tab]]. The packet path is a file. The path has no spaces.

## Out

`typed on /dev/ttysNNN` and exit 0 when inject landed.

`mac-inject-harness.sh takes a tty and a packet path` and exit 2 when an argument is missing.

`packet is ...` and exit 2 when the file is absent.

`packet path has a space: ...` and exit 2 when the path has a space.

Inject's own refusals pass through. A Window menu count other than one does not type the line.

## Ran

Awaiting a run.

## Then

The head has the packet as its first message. [[hop-80]] closes the tail. A workflow that is not hop-80 leaves the tail open.
