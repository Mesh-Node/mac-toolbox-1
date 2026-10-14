---
title: "Tool: close the tty"
type: tool
status: draft
evidence: verified-local
verified_on: "2026-10-12"
secrets: false
---

# close the tty

One Terminal tty. The address on the command line.

## Command

```
scripts/mac-close-tty.sh /dev/ttysNNN
```

The script writes the title token HOPCLOSE-<short> on that device, clicks the one Window menu item that contains the token, and sends Command-W. The Homebrew profile closes the tab on that keystroke. The script waits while that tty is still in the process list.

## In

`/dev/ttysNNN` or `ttysNNN`.

## Out

`closed /dev/ttysNNN` and exit 0 means that tty left the process list. The other tabs stay.

`refuse: /dev/ttysNNN still open` and exit 4 means the tty is still listed after Command-W. The working tab stays.

`refuse: no such tty: /dev/ttysNNN` and exit 4 means the device is already gone.

## Ran

2026-10-12, this Mac. Homebrew `warnOnShellCloseAction` is 0. `scripts/mac-close-tty.sh /dev/ttys001` sent Command-W and printed `closed /dev/ttys001` in 1 second. No sheet was up. The working session stayed on its own tty.

## Then

The working tab stays. See [[hop]].
