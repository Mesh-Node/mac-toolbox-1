---
title: "Schema"
type: foundation
status: draft
evidence: untested
verified_on: "2026-10-10"
secrets: false
---

# SCHEMA

Evidence labels (required on synthesized notes):

| Label | Meaning |
|---|---|
| `verified-local` | Observed on this Mac, with date and method |
| `verified-upstream` | Supported by linked official docs |
| `verified-both` | Local observation plus upstream source |
| `inferred` | Plausible, awaiting a check on this Mac |
| `untested` | Proposed procedure or config, awaiting a run |
| `obsolete` | Historical. Revalidate before use. |

## Write policy

Agent writes `inbox/` on their own: drafts and gaps.

Agent writes these after the operator says yes:

- `tools/`
- `toolchains/`
- `runbooks/`
- `decisions/`
- `foundations/`, and a broken link in a definition note
- `CHARTER.md`, this file, `index.md`, `tool.md`, `toolchain.md`

`raw/` is a sibling of `vault/`. It stays as ingested. Ingest starts when a file lands there.

## Secrets

`secrets: false` on every note. Credentials stay on the logged-in Mac, outside this folder.

## Provenance

```yaml
---
title: "..."
type: foundation | runbook | decision | instruction | draft
status: draft | verified | obsolete
evidence: verified-local | verified-upstream | inferred | untested
verified_on: YYYY-MM-DD
sources: []
secrets: false
---
```

A note in `tools/` is a [[tool]] when it points at a command that exists. A definition note names the idea. The command note is the tool.

## This vault vs the personal vault

This tree is the Mac operational toolbox. Personal notes stay in the personal vault. Mac notes stay in these rooms.

## Control preference

1. Terminal. `hermes`, `brew`, files, `osascript` for one Terminal tab or one tty.
2. Close one tty by address. That tty closes. The other tabs stay.
3. GUI is the last surface. Terminal opens the tab. This vault is read as files.

Mac notes use the Mac commands in `scripts/`.

## Deny list

Ask the operator, then:

- `brew install`, package upgrades, launch agents, Keychain, Full Disk Access grants
- Copy `~/.hermes`, `.env`, `auth.json`, or a GGUF into this tree
- Write a tool note after the command has run on this Mac
