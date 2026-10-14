---
title: "Mac Obsidian Toolbox"
type: agent-toolbox-charter
status: draft
version: "0.1.0"
created: "2026-10-10"
platform: "macOS"
owner: "Local AI Harness"
tags:
  - macos
  - obsidian
  - hermes
  - toolbox
agent_access:
  read: true
  draft_write: true
  direct_system_changes: false
  privileged_actions_require_approval: true
  external_actions_require_approval: true
source_policy:
  raw_sources_immutable: true
  synthesized_notes_require_provenance: true
  local_observations_timestamped: true
  secrets_permitted: false
secrets: false
evidence: untested
---

# Mac Obsidian Toolbox

## Purpose

This vault is the operational toolbox for a Mac Hermes harness.

It is a local, inspectable, Markdown-native knowledge system. Personal notes stay in the personal vault. This vault is the operational memory layer. The hop tools live in `tools/` and `toolchains/`.

A [[tool]] is a note. A [[toolchain]] is an ordered set of those notes. The executable lives in `scripts/`. Write a tool note when the command exists on this Mac and a human has run it.

## Pattern name

**Operational memory layer.** A memory module is a search tool plus the store it reads. This vault is the layer. Search comes when a tool note earns it.

- Externalized memory: durable knowledge lives in these notes.
- Retrieval: the agent reads these notes when needed.
- Procedural memory: a runbook lands here after it has been run.
- Decision memory: ADRs live in `decisions/` after operator review.
- Human-auditable: every claim can be opened, corrected, and linked.

## Operating principle

1. Read this vault and the filesystem first.
2. Use the terminal for inspection and for anything the shell can do.
3. Use `osascript` to open one Terminal tab or close one tty. One address.
4. The terminal does the job. GUI control is the last surface.
5. Verify, then write a note. A tool note points at a command that exists.

## Scope

This toolbox will document, once observed on the Mac:

- Hermes on this Mac: paths, health, model slots.
- Which model speaks. Chat default is Grok, via that Mac's own login. Embeddings that match the mesh are nomic-embed-text-v1.5 F16 at 768 dimensions. Settings, checks, and the Honcho pointer are in `../SETUP.txt`. A key stays on that Mac, outside this vault. Chat stays on Grok. The embedder stays on its own port.
- Obsidian conventions for this vault.
- Runbooks that have actually been run.

This toolbox holds:

- Notes, scripts, and `SETUP.txt`.
- Credentials stay on the logged-in Mac, outside this folder. See `../DENY.txt`.
- The hop chain in `tools/` and `toolchains/`.
- Personal notes stay in the personal vault.

## Evidence model

- `verified-local` — observed on this Mac, with date and method.
- `verified-upstream` — linked official documentation.
- `verified-both` — both.
- `inferred` — plausible, awaiting a check on this Mac.
- `untested` — proposed. This charter awaits a full read-through on a colleague Mac.
- `obsolete` — historical. Revalidate before use.

## Agent permissions

May, on their own:

- Read the vault.
- Draft in `inbox/`.
- Append a dated gap to `inbox/` when something is missing.

Ask the operator first, then:

- Write `tools/`, `toolchains/`, `runbooks/`, or `decisions/`.
- Install software, change login items, or touch Keychain.
- Run `sudo`, `brew install`, or any persistent service.
- Transmit data, or copy credentials.
- Use computer control.

## Structure

```text
macbook-toolbox/
├── START.txt
├── DENY.txt
├── raw/                         # disk evidence later. Sibling of the vault.
└── vault/
    ├── CHARTER.md
    ├── SCHEMA.md
    ├── index.md
    ├── tool.md                  # definition of a tool.
    ├── toolchain.md             # definition of a toolchain.
    ├── inbox/
    ├── foundations/
    ├── tools/                   # admitted tool notes
    ├── toolchains/              # admitted chain notes
    ├── runbooks/                # after a task has run
    └── decisions/               # after operator review
```

## First mission

Read the rooms, then read [[index]].

1. Read [[index]] and `../SETUP.txt`.
2. The current tools live in `tools/`. The scripts live in `scripts/`.
3. Record gaps in `inbox/`. Label a proposal `untested` until it has run.
4. A tool note waits until its command exists.

## Definition of success

The operator can open this vault and see:

- What a tool is, and that [[new-tab]] [[inject]] [[hop]] [[deliver]] [[close-the-tty]] are the current tools.
- What a toolchain is. The only toolchain is [[hop-80]].
- Where a draft goes: `inbox/`.
- That chat is Grok, logged in on that Mac, and the checks are in `../SETUP.txt`.

## Agent opening instruction

You are the steward of this Mac toolbox. Treat it as an operational memory layer. Act from the notes that are here.

Prefer inspection. A tool note waits until its command exists. When an action would change the Mac, ask, then proceed.
