---
title: "How a tool is admitted"
type: instruction
status: draft
evidence: verified-local
verified_on: "2026-10-10"
secrets: false
---

# How a tool is admitted

This page is the pattern. The only toolchain is [[hop-80]]. This vault holds the Mac toolbox.

## Tool

A file in `tools/`. Frontmatter `type: tool`. One command pointer. In. Out. What ran, with a date. `Then` names the next note.

The note is the tool. The script lives in `scripts/`.

Write the note when the command exists. A command awaiting a run on the target machine keeps `evidence: untested`, and the Ran section says it is awaiting a run.

## Toolchain

A file in `toolchains/`. Frontmatter `type: chain` and a `tools:` list in order. The body is that order in sentences. A wrapper script comes after the order has been run by hand.

A sentence that says "and then" is already a toolchain. It lives in `toolchains/`.

## Admission holds

- A tool note, authored, pointing at a command.
- A chain note, separate from a journal.

An empty-room marker comes out once the real tool is admitted. One note per tool.

## This vault, now

Admitted now:

- [[new-tab]]
- [[inject]]
- [[hop]]
- [[deliver]]
- [[close-the-tty]]

The only toolchain is [[hop-80]].

`foundations/`, `runbooks/`, and `decisions/` wait for observed notes.
