[< CV8 Runtime Expansion](../index.md)

# CV8.E2 — Codex Runtime Implementation

**Epic:** Add a Codex runtime adapter that calls the shared Python core without duplicating Mirror Mind behavior
**Status:** Draft
**Depends on:** CV8.E1 Codex Runtime Spike

---

## What This Is

This epic implements the Codex integration at the highest honest parity level
selected by CV8.E1. The adapter must stay thin. Codex-specific files may map
runtime events, parse runtime payloads, and call `uv run python -m memory ...`.
They must not reimplement identity loading, routing, extraction, journey logic,
tasks, or storage.

The implementation should follow the existing principle:

> Python/CLI owns database and core behavior. The runtime owns event plumbing and
> filesystem-native interaction.

---

## Done Condition

- Codex runtime files exist in the correct project-local location discovered by
  CV8.E1
- Codex session start calls `uv run python -m memory conversation-logger session-start`
- Codex user turns are logged with `--interface codex`
- Codex assistant turns are logged explicitly, or backfilled from transcript if
  Codex exposes transcript paths
- Codex session end closes the runtime session and triggers backup
- Codex Mirror Mode loads context through `uv run python -m memory mirror load`
  where supported
- Codex Builder Mode can call `uv run python -m memory build load <slug>` and
  then use Codex-native file reading for project docs
- Codex command surface covers the agreed minimum command set from CV8.E1
- implementation has unit or integration tests for every Python-side contract
  change

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E2.S1 | Add `codex` interface support in CLI/service tests and reporting surfaces | Draft |
| CV8.E2.S2 | Implement Codex session lifecycle adapter | Draft |
| CV8.E2.S3 | Implement Codex user and assistant message logging path | Draft |
| CV8.E2.S4 | Implement Codex Mirror Mode context loading path | Draft |
| CV8.E2.S5 | Implement Codex command/skill surface for core Mirror Mind commands | Draft |
| CV8.E2.S6 | Implement Codex Builder Mode command flow | Draft |

---

## Minimum Command Surface

The exact runtime spelling depends on Codex. The semantic surface should include:

- mirror mode: `mm-mirror`
- builder mode: `mm-build <journey>`
- journeys: `mm-journeys`, `mm-journey <slug>`
- tasks: `mm-tasks`
- memory inspection: `mm-memories`, `mm-conversations`, `mm-recall`
- session control: `mm-new`, `mm-mute`
- identity: `mm-seed`, `mm-identity`
- utilities: `mm-consult`, `mm-backup`, `mm-help`

If Codex cannot expose all of these as native commands, the missing commands are
documented in CV8.E3 and the parity level is adjusted.

---

## Design Constraints

- No Codex-specific business logic
- No direct SQLite access from Codex files
- No runtime-specific copy of skill algorithms
- No hidden production DB access in tests or smoke scripts
- All Python commands inside the repo use `uv run`

---

## See also

- [CV8.E1 Codex Runtime Spike](../cv8-e1-codex-runtime-spike/index.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
