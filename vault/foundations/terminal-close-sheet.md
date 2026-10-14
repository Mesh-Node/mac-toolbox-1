---
title: "Terminal close sheet"
type: foundation
status: draft
evidence: verified-local
verified_on: "2026-10-14"
secrets: false
---

# Terminal close sheet

A person sets this. The scripts do not. Trainees learn the click, then learn how to change it.

## Set it

1. Open Terminal.
2. Terminal menu, Settings. On older macOS the menu says Preferences.
3. Profiles. Select the profile new tabs use. On this Mac that profile is Homebrew. A new Mac may say Basic. Use the profile named in the General pane as the default.
4. Shell.
5. When the shell exits: Close the window.
6. Ask before closing: Never.
7. Close Settings. Open a new tab. It should use that profile.

Command-W from [[close-the-tty]] closes the tab when those two menus are set that way. A sheet means the close did not finish. Go back to Shell and set Ask before closing to Never.

## Change it later

Same screen. Profiles, the profile new tabs use, Shell.

- To bring the sheet back, set Ask before closing to Always, or to Only if there are processes other than the login shell and its children.
- To keep the window after the shell exits, set When the shell exits to Don't close the window.

A change applies to new tabs of that profile. An open tab keeps the profile it already has.

## This Mac

Observed 2026-10-14. Default profile and startup profile are Homebrew. Ask before closing is Never. When the shell exits, the window closes. The person set this by hand.

See `../SETUP.txt`.
