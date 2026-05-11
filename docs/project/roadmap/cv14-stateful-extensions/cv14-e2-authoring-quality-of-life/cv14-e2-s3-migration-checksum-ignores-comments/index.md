[CV14.E2](../index.md) › **S3 Migration checksum ignores comments and whitespace**

# CV14.E2.S3 — Migration checksum ignores comments and whitespace

**Status:** ✅ Done · 2026-05-11

## Problem

`memory.extensions.migrations.run_migrations` hashes each migration's
**raw bytes** and refuses to re-run a file whose hash has drifted from
the recorded one. The intent is right (a structural edit to an applied
migration is dangerous), but the granularity is too fine: adding a
`-- note for future me` line to an already-applied migration counts as
drift. The author then has to either revert the comment or hand-edit
`_ext_migrations.checksum`.

Both options are bad: reverting punishes documentation; hand-editing
the bookkeeping table is exactly the kind of out-of-band change the
guard was supposed to prevent.

## Plan

- Introduce a `_normalised_checksum(sql)` helper that hashes the SQL
  **after** stripping comments (`--` and `/* ... */`) and collapsing
  whitespace. The existing `_strip_noise` strips comments and string
  literals for prefix inspection; we re-use the comment-stripping
  part and add whitespace normalisation, but **keep string literals
  intact** because they are real SQL content.
- Store the normalised checksum (no schema migration needed: the
  column is `TEXT`, the new hashes are still 64 hex chars).
- Backwards compatibility: if an existing recorded checksum matches
  neither the new normalised hash nor the old raw hash, the drift
  guard triggers exactly as today. If it matches the **raw** hash
  but not the normalised one, the runner silently upgrades the
  stored value to the normalised one (one-time, idempotent).
- Document the contract in
  `docs/product/extensions/migrations.md`: comment and whitespace
  edits are allowed and ignored; any change to the SQL semantics
  still trips the guard.

## Test Guide

- Apply a migration → checksum recorded.
- Add a `-- comment` to the file → second run is a no-op (no error,
  no second insert).
- Reformat whitespace (extra blank lines, trailing spaces, indent
  changes) → second run is a no-op.
- Add a structural change (`ALTER TABLE ...`) → second run raises
  `ExtensionMigrationError` with the existing drift message.
- Pre-existing recorded checksum that matches the **raw** hash of
  the unchanged file is silently upgraded to the normalised hash on
  the next run (backwards-compat path).
- Edits inside a string literal still trip the guard — e.g. changing
  `INSERT INTO ext_x_table VALUES ('a')` to `... ('b')` is real
  drift, even though the comment stripping would not have removed
  anything.

## Acceptance

- Tests pass.
- Real extension can edit a comment in an already-applied migration
  and re-install with no manual intervention.
- Migrations doc updated.
