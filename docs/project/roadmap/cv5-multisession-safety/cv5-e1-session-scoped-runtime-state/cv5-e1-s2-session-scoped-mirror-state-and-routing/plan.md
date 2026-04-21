[< CV5.E1 Session-Scoped Runtime State](../index.md)

# CV5.E1.S2 — Plan — Session-Scoped Mirror State and Routing

## Goal

Replace singleton mirror routing state with session-scoped state so mirror mode
activation, reinjection, and conversation switching do not bleed across
simultaneous sessions.

## Design

- make mirror state helpers accept explicit `session_id`
- persist mirror state in the runtime session registry instead of one global
  `mirror_state.json`
- update mirror skill functions to accept optional `session_id`
- update conversation logger helpers to route via explicit session id whenever
  available
- retain compatibility fallbacks only where a runtime truly cannot pass a
  session id yet

## Implementation Notes

- prefer explicit `session_id` parameters on Python APIs over implicit globals
- keep `context_only` behavior intact
- preserve the user-visible CLI surface where possible

## Verification

- unit tests proving two sessions can hold different mirror state simultaneously
- hook helper tests for `needs-inject`, `get`, and `mark-injected` by session
- conversation logger tests for `switch_conversation` and assistant logging by session
