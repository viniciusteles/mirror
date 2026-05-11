# Migrations

> Replace this template with the actual migration history of the extension.

Maintain a chronological list of migrations with a one-line rationale each.
The list is the canonical history; the SQL files are the implementation.

| File | Date | Summary |
|---|---|---|
| `001_init.sql` | YYYY-MM-DD | Initial schema. Defines all base tables. |
| `002_add_<column>.sql` | YYYY-MM-DD | Adds X to support Y. See US-NN. |

For each non-trivial migration, add a section below with:

- **Why.** What problem prompted the change.
- **What changed.** Tables, columns, indices, FKs.
- **Backfill.** If existing rows needed to be populated, how.
- **Compatibility.** Does the change require updates to other parts of
  the extension or to user data on disk? Note them.

## Anti-patterns recorded here

If a migration was rolled forward to undo a previous one, note it. Future
readers will want to know that `005_drop_X.sql` exists because `003_add_X.sql`
turned out to be a mistake, with a link to the user story that recorded the
decision.

## Schema version

If the extension uses `ext_<id>_meta.schema_version`, document the current
value and what it means.
