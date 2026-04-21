[< CV5.E1 Session-Scoped Runtime State](../index.md)

# CV5.E1.S1 — Plan — Runtime Session Registry

## Goal

Introduce a SQLite-backed runtime session registry so the authoritative mapping
between `session_id` and `conversation_id` is no longer stored in
`session_map.json`.

## Design

- add a `runtime_sessions` table to the main schema
- persist one row per runtime session id
- store enough state to support routing and mirror mode:
  - `session_id`
  - `conversation_id`
  - `interface`
  - `mirror_active`
  - `persona`
  - `journey`
  - `hook_injected`
  - timestamps / metadata
- add store helpers for fetch/update/upsert by `session_id`
- keep the database as the source of truth; JSON files become deprecated or
  best-effort compatibility only

## Implementation Notes

- prefer transactional helpers over external read-modify-write logic
- keep the table generic enough for both Claude Code and Pi
- avoid adding a separate service layer unless it improves clarity materially

## Risks

- accidental duplication between conversation metadata and runtime session state
- partial migration where some code still reads old files
- schema changes without enough tests for existing commands

## Verification

- unit tests for runtime session store helpers
- conversation logger tests proving session mapping is DB-backed
- concurrent session creation test proving no lost mappings
