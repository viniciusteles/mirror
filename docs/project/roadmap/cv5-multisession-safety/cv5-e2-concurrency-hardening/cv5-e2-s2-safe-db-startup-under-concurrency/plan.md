[< CV5.E2 Concurrency Hardening](../index.md)

# CV5.E2.S2 — Plan — Safe DB Startup Under Concurrency

## Goal

Prevent avoidable startup failures when multiple processes open the same mirror
home at the same time.

## Design

- make migration bookkeeping idempotent under concurrency
- set pragmatic SQLite connection settings for shared access
- ensure new-database initialization and migration application tolerate races
  without raising integrity failures for already-applied steps

## Verification

- concurrent startup regression test against a fresh temporary database
- no `UNIQUE constraint failed: _migrations.id` during simultaneous open
