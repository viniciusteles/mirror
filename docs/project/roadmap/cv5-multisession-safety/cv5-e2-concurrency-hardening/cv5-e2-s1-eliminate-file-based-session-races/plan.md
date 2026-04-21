[< CV5.E2 Concurrency Hardening](../index.md)

# CV5.E2.S1 — Plan — Eliminate File-Based Session Races

## Goal

Remove race-prone read-modify-write session routing behavior from JSON files.

## Design

- stop treating `session_map.json` as the authoritative mapping
- replace file-backed session lookup/update with transactional SQLite helpers
- keep any remaining file use limited to diagnostics or legacy fallback paths
- ensure backfill/import flows also use the runtime session registry

## Verification

- concurrent test that used to lose session map entries now preserves all sessions
- logger behavior still works for normal sequential usage
