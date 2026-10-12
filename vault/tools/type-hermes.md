---
title: "Tool: type hermes"
type: tool
status: draft
evidence: verified-local
verified_on: "2026-10-12"
secrets: false
---

# type hermes

Type `hermes` and Return into the tty argument. The address is the `new=` line from [[new-tab]].

The file is POSIX shell. It calls [[inject]] with that tty and the line `hermes`.

## Command

```
scripts/mac-type-hermes.sh /dev/ttysNNN
```

## In

The new tty printed by [[new-tab]].

## Out

The print and the exit come from [[inject]]. A missing address prints `mac-type-hermes.sh takes one tty address` and exits 2.

## Lines

The numbers are the lines in `scripts/mac-type-hermes.sh`.

1. `#!/bin/sh` starts the file with the POSIX shell.
2. The comment names the job: type hermes and Return into the tty argument.
3. The comment says the address is the `new=` line from mac-new-tab.sh.
4. `set -eu` stops the script on an unset name or a failed command.
5. `ADDR=${1:-}` reads the tty argument.
6. A missing address prints `mac-type-hermes.sh takes one tty address` and exits 2.
7. `ROOT` is the directory that holds this script.
8. `exec` runs `mac-inject.sh` with that tty and the line `hermes`. This script ends there.

## Ran

2026-10-12, this Mac. `scripts/mac-type-hermes.sh /dev/ttys012` printed `typed on /dev/ttys012` and exited 0. Hermes pid 95992 is on ttys012. This session stayed on ttys001, pid 93112.

The previous file searched for a blank tab. On 2026-10-12 that search found ttys012, and a later run from ttys013 was followed by Hermes on ttys014. Those runs are not this file.

## Then

The chain calls this with `"$new"` when the line to type is `hermes`. Any other line goes to [[inject]] with `"$new"`.
