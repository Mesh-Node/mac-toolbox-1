---
title: "Tool: new tab"
type: tool
status: draft
evidence: verified-local
verified_on: "2026-10-12"
secrets: false
---

# new tab

Open one Terminal tab and print two tty numbers. `head` is the tab Command-T opened. `tail` is the tty of the session that ran this script.

The file is POSIX shell, started by `#!/bin/sh`. It is not Bash. The block between `APP` markers is AppleScript. `osascript` runs that block.

The chain stores the two printed lines. A name set inside this script dies when the script exits. The caller keeps the names.

```
eval "$(scripts/mac-new-tab.sh)"
```

After that line, `$head` and `$tail` exist in the chain shell. Inject receives `"$head"`. Close receives `"$tail"`.

## Command

```
scripts/mac-new-tab.sh
```

## In

Terminal is already running. This script is launched from the tail tty.

## Out

```
head=/dev/ttysNNN
tail=/dev/ttysNNN
```

Exit 0. The script starts no command in the new tab.

`tail tty was not found` and exit 4 when the parent walk finds no Terminal tty.

`head tty was not found` and exit 4 when Command-T does not add exactly one Terminal tty.

`mac-new-tab.sh runs on Darwin` and exit 5 on another system.

## Lines

The numbers are the lines in `scripts/mac-new-tab.sh`.

1. `#!/bin/sh` starts the file with the POSIX shell.
2. The comment names the job: open one tab and print head and tail.
3. The comment says the chain stores those two lines and later tools receive them as arguments.
4. `set -eu` stops the script on an unset name or a failed command.
5. `case "$(uname -s)"` reads the operating system name.
6. `Darwin)` continues on macOS.
7. Any other system prints `mac-new-tab.sh runs on Darwin` and exits 5.
8. `esac` ends the system check.
9. A blank line.
10. The comment says the next function reads the tty of this process when this process sits in a Terminal tab.
11. `tail_tty()` starts that function.
12. `pid=$$` starts the walk at this process.
13. `i=0` counts the steps of the walk.
14. The loop continues while the process is not launchd and the walk is under 16 steps.
15. `ps -o tty=` reads the tty of the current process. Spaces are removed.
16. `case` checks that tty name.
17. A name like `ttys001` is printed, and the function returns success.
18. `esac` ends the tty check.
19. `ps -o ppid=` moves the walk to the parent process.
20. An empty parent ends the walk.
21. `i=$((i + 1))` counts the step.
22. `done` ends the loop.
23. `return 1` means this process has no Terminal tty.
24. `}` ends the function.
25. A blank line.
26. The comment says the next function lists every tty whose ancestor is Terminal.app.
27. `terminal_ttys()` starts that function.
28. `ps` starts the process list. The awk program follows.
29. The awk marks the Terminal process id.
30. The awk stores each process parent, and stores a tty name when the third field is a tty.
31. `END` runs after every process line has been read.
32. The awk visits each process that has a tty.
33. `q = p` starts the parent walk at that process.
34. `seen = 0` counts the steps of that walk.
35. The walk continues while the process is not launchd and the walk is under 24 steps.
36. When Terminal is an ancestor, the awk prints that tty and stops the walk.
37. `q = parent[q]` moves to the parent.
38. `seen++` counts the step.
39. `}` ends the walk body.
40. `}` ends the process loop.
41. `}` ends the awk program.
42. `sort -u` keeps each tty once.
43. `}` ends the function.
44. A blank line.
45. `TAIL=$(tail_tty)` stores the tail tty. A missing tail prints `tail tty was not found` and exits 4.
46. `BEFORE=$(terminal_ttys)` stores the Terminal tty list before Command-T.
47. A blank line.
48. The comment names the next job: bring Terminal to the front, then send Command-T.
49. `osascript <<'APP'` hands the following lines to osascript. The quotes keep the shell from changing them.
50. `tell application "System Events"` asks System Events to drive the screen.
51. `tell process "Terminal"` selects the Terminal process.
52. `set frontmost to true` brings Terminal to the front.
53. `keystroke "t" using command down` presses Command-T. That opens one tab in the front Terminal window.
54. `end tell` ends the Terminal block.
55. `end tell` ends the System Events block.
56. `APP` ends the text handed to osascript.
57. A blank line.
58. The comment says the new tty is the Terminal tty that was not in the list before Command-T.
59. `before_f=$(mktemp)` makes a file for the before list.
60. `now_f=$(mktemp)` makes a file for the after list.
61. `trap` removes those two files when the script exits.
62. The before list is written to `before_f`, one tty per line.
63. `NEW=""` holds the new tty.
64. `i=0` counts the waits.
65. The loop waits up to 20 times for exactly one new tty.
66. `NOW=$(terminal_ttys)` reads the Terminal tty list again.
67. That list is written to `now_f`.
68. `comm -13` prints the tty that is in the after list and not in the before list. `head` keeps the first one.
69. `COUNT` is how many new ttys appeared.
70. One new tty ends the wait.
71. `break` leaves the loop.
72. `fi` ends the one-tty test.
73. `NEW=""` clears a partial result so the next wait starts clean.
74. `i=$((i + 1))` counts the wait.
75. `sleep 0.25` waits a quarter second for the new tty to appear.
76. `done` ends the wait.
77. A blank line.
78. A missing head tty prints `head tty was not found` and exits 4.
79. A blank line.
80. `printf 'head=/dev/%s'` prints the head tty.
81. `printf 'tail=/dev/%s'` prints the tail tty.
82. `exit 0` ends the script after those two lines.

## Ran

2026-10-12, this Mac. The previous file printed `new=/dev/ttys012` and `donor=/dev/ttys001`. That run is not this file. This file prints `head=` and `tail=`.

Earlier runs of the previous file, which printed nothing, opened a tab at 07:38 and opened ttys013 later the same day. Those runs are not this file.

## Then

The chain passes `"$head"` to [[inject]]. `"$tail"` is the tty for a later action, including close.
