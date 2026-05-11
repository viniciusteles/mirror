# Legacy migration

> Replace this template if the extension can ingest data from an older
> system. Delete the file otherwise.

Document the procedure for moving data from a previous implementation into
this extension's schema. The reader is the user, not the author.

Sections to include:

- **Scope.** Which entities are migrated. Which are not, and why.
- **Source.** Where the legacy data lives (file path, DB, format).
- **Prerequisites.** What must be installed and configured first.
- **Dry run.** A command that reports what would be migrated without
  writing anything. Always provide one.
- **Apply.** The actual migration command.
- **Verification.** How to confirm the migration succeeded: row counts,
  spot checks, sample queries.
- **Rollback.** What to do if the migration produces wrong results. Almost
  always: drop the extension's tables, restore from backup, re-run the
  migration after fixing the bug.

If embeddings are part of the migration, note whether they can be reused
(same model) or must be regenerated (model changed).

Mention any **invariants** the migration restores or breaks compared to
the legacy system.

Always recommend a backup before the user runs the apply step.
