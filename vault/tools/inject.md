---
title: "Tool: inject"
type: tool
status: draft
evidence: verified-local
verified_on: "2026-10-12"
secrets: false
---

# inject

Type one line into one Terminal tab and press Return. The tty is the argument. The line is the second argument.

The file is POSIX shell, started by `#!/bin/sh`. It is not Bash. The block between `APP` markers is AppleScript. `osascript` runs that block.

The title token is the label that lets the Window menu select that tty. Command-W and a keystroke have no tty argument. They land in the front tab. The token makes the named tty the front tab before the line is typed.

## Command

```
scripts/mac-inject.sh /dev/ttysNNN 'the line'
```

## In

The tty is `"$new"` from [[new-tab]]. The line is the text to type.

## Out

`typed on /dev/ttysNNN` and exit 0 when the Window menu showed one item for the token and the line was typed.

`mac-inject.sh takes a tty and a line` and exit 2 when an argument is missing.

`mac-inject.sh takes one tty address: ...` and exit 2 when the address is not one tty.

`tty is /dev/ttysNNN` and exit 4 when that device is absent.

`mac-inject.sh runs on Darwin` and exit 5 on another system.

The AppleScript stops with `Window menu hits for TYPE-ttysNNN is N` when the Window menu does not show exactly one item for that token.

## Lines

The numbers are the lines in `scripts/mac-inject.sh`.

1. `#!/bin/sh` starts the file with the POSIX shell.
2. The comment names the job: type one line into one Terminal tab and press Return.
3. The comment names the arguments: the tty, then the line.
4. `set -eu` stops the script on an unset name or a failed command.
5. `ADDR=${1:-}` reads the tty argument.
6. `TEXT=${2:-}` reads the line argument.
7. Both arguments must be present. A missing argument prints `mac-inject.sh takes a tty and a line` and exits 2.
8. `case` checks the tty shape.
9. `/dev/ttysNNN` or `ttysNNN` continues.
10. Any other address prints `mac-inject.sh takes one tty address` and exits 2.
11. `esac` ends the address check.
12. `case "$(uname -s)"` reads the operating system name.
13. `Darwin)` continues on macOS.
14. Any other system prints `mac-inject.sh runs on Darwin` and exits 5.
15. `esac` ends the system check.
16. `SHORT=${ADDR#/dev/}` keeps the tty name without `/dev/`.
17. The device `/dev/$SHORT` must exist. A missing device prints `tty is /dev/$SHORT` and exits 4.
18. A blank line.
19. The comment says the title token makes this tty one Window menu item. The write is display, not a command.
20. `TOKEN="TYPE-$SHORT"` builds that title, for example `TYPE-ttys013`.
21. `printf` writes the title escape to that device. The tab title changes. No command runs.
22. A blank line.
23. `osascript` runs the AppleScript and passes the token and the line as arguments.
24. `on run argv` starts the AppleScript with that argument list.
25. `set token to item 1 of argv` reads the token.
26. `set commandLine to item 2 of argv` reads the line to type.
27. `tell application "System Events"` asks System Events to drive the screen.
28. `tell process "Terminal"` selects the Terminal process.
29. `set frontmost to true` brings Terminal to the front.
30. `set hits to 0` starts the match count.
31. `set tries to 0` starts the wait count.
32. The repeat waits up to 8 times for exactly one Window menu item to contain the token.
33. Each wait resets the match count.
34. `tell menu "Window"` opens the Window menu list.
35. The inner repeat visits each menu item.
36. `set n to name of mi` reads the item name.
37. A missing name becomes an empty string.
38. A name that contains the token increases the match count.
39. `end repeat` ends the item walk.
40. `end tell` ends the Window menu read.
41. One match ends the wait.
42. `set tries to tries + 1` counts a wait.
43. `delay 0.25` waits a quarter second for the title to appear in the menu.
44. `end repeat` ends the wait.
45. A match count other than one stops the AppleScript with `Window menu hits for TYPE-ttysNNN is N`.
46. The script returns to the Window menu to click.
47. It walks the items again.
48. It reads each name.
49. A missing name becomes an empty string.
50. The item whose name contains the token is the tab.
51. `click mi` selects that tab. The keystroke will land there.
52. `exit repeat` stops after that one click.
53. `end if` ends the token test.
54. `end repeat` ends the click walk.
55. `end tell` ends the click menu.
56. `delay 0.3` waits for that tab to be front.
57. `keystroke commandLine` types the line.
58. `keystroke return` presses Return.
59. `delay 0.3` waits, then a second Return is sent.
60. `keystroke return` presses Return again. That second press is the submit.
61. `end tell` ends the Terminal block.
62. `end tell` ends the System Events block.
63. `end run` ends the AppleScript.
64. `APP` ends the text handed to osascript.
65. A blank line.
66. `echo "typed on /dev/$SHORT"` prints the tab that received the line.
67. `exit 0` ends the script after that print.

## Ran

2026-10-12, this Mac. `scripts/mac-inject.sh /dev/ttys013` typed this line and printed `typed on /dev/ttys013`. The exit was 0.

`/Users/marksnowjr/Documents/macbook-toolbox/scripts/mac-new-tab.sh && sleep 1 && /Users/marksnowjr/Documents/macbook-toolbox/scripts/mac-type-hermes.sh`

That line ran in ttys013. A new tty appeared, ttys014. Hermes pid 78189 is on ttys014. This session stayed on ttys001, pid 93112.

2026-10-12, this Mac. After the hop packet was typed into ttys013, a separate Return was sent to that tab. The keystroke exited 0. This session stayed on ttys001, pid 93112. The second Return now in the file was not part of that keystroke.

## Then

The donor for the close is ttys014. This session stays on ttys001.
