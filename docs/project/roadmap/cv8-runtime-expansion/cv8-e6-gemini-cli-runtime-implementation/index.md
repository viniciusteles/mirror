[< CV8 Runtime Expansion](../index.md)

# CV8.E6 — Gemini CLI Runtime Implementation

**Epic:** Add a Gemini CLI runtime adapter that calls the shared Python core without duplicating Mirror Mind behavior
**Status:** Draft
**Depends on:** CV8.E5 Gemini CLI Runtime Spike

---

## What This Is

This epic implements the Gemini CLI integration at the highest honest parity
level selected by CV8.E5. The adapter should reuse the runtime patterns hardened
after Codex and avoid creating a second one-off implementation.

As with Codex, Gemini-specific files may map runtime events, parse payloads, and
call `uv run python -m memory ...`. They must not own Mirror Mind behavior.

---

## Done Condition

- Gemini CLI runtime files exist in the correct project-local location discovered
  by CV8.E5
- Gemini CLI session start calls `uv run python -m memory conversation-logger session-start`
- Gemini CLI user turns are logged with `--interface gemini_cli`
- Gemini CLI assistant turns are logged explicitly, or backfilled from transcript
  if Gemini CLI exposes transcript paths
- Gemini CLI session end closes the runtime session and triggers backup
- Gemini CLI Mirror Mode loads context through `uv run python -m memory mirror load`
  where supported
- Gemini CLI Builder Mode can call `uv run python -m memory build load <slug>`
  and then use Gemini CLI-native file reading for project docs
- Gemini CLI command surface covers the agreed minimum command set from CV8.E5
- implementation has unit or integration tests for every Python-side contract
  change

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E6.S1 | Add `gemini_cli` interface support in CLI/service tests and reporting surfaces | Draft |
| CV8.E6.S2 | Implement Gemini CLI session lifecycle adapter | Draft |
| CV8.E6.S3 | Implement Gemini CLI user and assistant message logging path | Draft |
| CV8.E6.S4 | Implement Gemini CLI Mirror Mode context loading path | Draft |
| CV8.E6.S5 | Implement Gemini CLI command/skill surface for core Mirror Mind commands | Draft |
| CV8.E6.S6 | Implement Gemini CLI Builder Mode command flow | Draft |

---

## Minimum Command Surface

The exact runtime spelling depends on Gemini CLI. The semantic surface should
include:

- mirror mode: `mm-mirror`
- builder mode: `mm-build <journey>`
- journeys: `mm-journeys`, `mm-journey <slug>`
- tasks: `mm-tasks`
- memory inspection: `mm-memories`, `mm-conversations`, `mm-recall`
- session control: `mm-new`, `mm-mute`
- identity: `mm-seed`, `mm-identity`
- utilities: `mm-consult`, `mm-backup`, `mm-help`

If Gemini CLI cannot expose all of these as native commands, the missing
commands are documented in CV8.E7 and the parity level is adjusted.

---

## Design Constraints

- No Gemini-specific business logic
- No direct SQLite access from Gemini CLI files
- No runtime-specific copy of skill algorithms
- No hidden production DB access in tests or smoke scripts
- All Python commands inside the repo use `uv run`

---

## See also

- [CV8.E5 Gemini CLI Runtime Spike](../cv8-e5-gemini-cli-runtime-spike/index.md)
- [CV8.E4 Runtime Adapter Hardening](../cv8-e4-runtime-adapter-hardening/index.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
