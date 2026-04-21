# English Domain Language Migration Plan

Date: 2026-04-16

Checkpoint tag:

```text
pre-english-domain-migration
```

## Purpose

This plan defines how to migrate the project fully from the remaining
Portuguese domain language to English. The goal is to make English the language
of the public API, persisted schema, identity data, filesystem state, commands,
documentation, and active implementation.

This is a migration plan, not a broad rename checklist. The risky parts are
persisted databases, local filesystem state, and user-facing command contracts.
Those must move with tests and compatibility behavior.

## Target Vocabulary

| Current | Target | Notes |
| --- | --- | --- |
| `memoria` | `memory` | Package and legacy database terminology. |
| `espelho` | `mirror` | API, config, docs, and storage directory language. |
| `travessia` | `journey` | Primary domain concept. |
| `travessia_id` | `journey_id` | Foreign-key style identifier. |
| `caminho` | `journey_path` | Use when it means a path through a journey. Use plain `path` only for filesystem paths. |
| `conversa` | `conversation` | Compatibility/client/docs terminology. |
| `tarefa` | `task` | Compatibility/client/docs terminology. |
| `anexo` | `attachment` | Compatibility/client/docs terminology. |
| `identidade` | `identity` | Compatibility/client/docs terminology. |

## Principles

- Preserve existing user data during the migration.
- Keep migration and compatibility removal as separate commits.
- Do not rewrite old migration history unless there is a clear reason. Add new
  forward migrations.
- Add tests before changing persisted schema or filesystem behavior.
- Prefer explicit compatibility paths over clever dynamic behavior.
- Leave historical session logs intact, except for optional explanatory notes.
- Stop after each high-risk track for review before continuing.

## Compatibility Policy

During the migration:

- New code should use English names only.
- Existing Portuguese persisted data should be migrated forward.
- Existing Portuguese filesystem locations should be discovered safely until the
  runtime compatibility removal checkpoint.
- Existing Portuguese identity YAML keys should be readable until the repository
  data has moved.
- Existing Portuguese CLI flags may remain as deprecated aliases for one
  compatibility window if that is cheap and clear.

After the migration is verified:

- Portuguese compatibility APIs, CLI aliases, runtime identity fallbacks, and
  legacy storage discovery are removed.
- `src/memoria/` is removed.
- Only migration tooling/tests and historical documentation references keep old
  names.

## Migration Tracks

### 1. Characterization And Migration Tests

Add tests before changing behavior.

Required coverage:

- current schema with `travessia` and `travessia_id` migrates to `journey` and
  `journey_id`
- existing rows keep their values after migration
- identity layer values migrate from `travessia` and `caminho` to `journey` and
  `journey_path`
- old identity YAML key `travessia_id` is accepted during the transition
- new identity YAML key `journey_id` is preferred
- old storage location is discovered when the new storage location does not
  exist
- both old and new storage locations existing at the same time does not
  silently overwrite data
- deprecated CLI flags either map to English arguments or intentionally fail
  with a clear message

Suggested files:

- `tests/unit/memory/db/test_english_schema_migration.py`
- `tests/unit/memory/test_config_paths.py`
- `tests/unit/memory/services/test_identity.py`
- `tests/unit/memory/cli/`

### 2. SQLite Schema And Storage

Add a new forward migration.

Target schema changes:

- `conversations.travessia` -> `conversations.journey`
- `memories.travessia` -> `memories.journey`
- `tasks.travessia` -> `tasks.journey`
- `attachments.travessia_id` -> `attachments.journey_id`
- `idx_memories_travessia` -> `idx_memories_journey`
- `idx_tasks_travessia` -> `idx_tasks_journey`
- `idx_attachments_travessia` -> `idx_attachments_journey`
- `idx_attachments_travessia_name` -> `idx_attachments_journey_name`
- identity layer values `travessia` -> `journey`
- identity layer values `caminho` -> `journey_path`

Implementation notes:

- SQLite supports column rename in modern versions, but table rebuilds may be
  safer if index or constraint handling becomes unclear.
- The migration should be idempotent enough for partially migrated local
  databases.
- Update schema creation for fresh databases and migration logic for existing
  databases in the same commit.
- Keep an old-schema fixture or test setup that proves real migration behavior.

Primary files:

- `src/memory/db/schema.py`
- `src/memory/db/migrations.py`
- `src/memory/models.py`
- `src/memory/storage/store.py`

Production rehearsal:

- Before opening the app against a production database, rehearse the migration
  against a copy:

```text
memory-rehearse-migration
```

- The default command resolves the configured production database path without
  importing `memory.config`, so it does not copy legacy databases or run
  migrations against the real database as a side effect.
- To make the source and output explicit:

```text
memory-rehearse-migration \
  --db-path ~/.espelho/memory.db \
  --output-dir /tmp/memory-migration-rehearsals
```

- If the production database still uses the legacy name:

```text
memory-rehearse-migration \
  --db-path ~/.espelho/memoria.db \
  --output-dir /tmp/memory-migration-rehearsals
```

- The rehearsal copies the database and any `-wal`/`-shm` sidecars, runs the
  normal migration path against the copy, verifies English columns/indexes and
  row counts, and reports the copied database path.
- The app should be stopped while making the rehearsal copy. The rehearsal tool
  does not mutate the source database, but an actively changing SQLite database
  can still produce an inconsistent file copy.

### 3. Identity Data And Loading

Move repository identity data to English names.

Target changes:

- `identity/travessias/` -> `identity/journeys/`
- YAML key `travessia_id` -> `journey_id`
- layer `travessia` -> `journey`
- layer `caminho` -> `journey_path`

Compatibility behavior:

- The loader should accept `travessia_id` while normalizing to `journey_id`.
- If both keys exist, `journey_id` should win unless the values conflict.
- If values conflict, fail clearly instead of guessing.

Primary files:

- `identity/`
- `src/memory/services/identity.py`
- identity service tests

### 4. Filesystem And Config

Move mirror storage language to English.

Target changes:

- `DEFAULT_ESPELHO_DIR` -> `DEFAULT_MIRROR_DIR`
- default directory `~/.espelho` -> `~/.mirror-poc`
- keep `MEMORY_DIR`, `MEMORY_PROD_DIR`, `DB_PATH`, and `DB_BACKUP_PATH` because
  they are already English
- keep legacy database copy behavior for `memoria*.db` until compatibility
  removal

Compatibility behavior during the migration:

- New installs use `~/.mirror-poc`.
- If `~/.mirror-poc` does not exist and `~/.espelho` exists, use or migrate
  from `~/.espelho`.
- If both exist, prefer the explicit environment configuration if present.
- If both exist without explicit configuration, do not merge silently. The code
  should choose a predictable path and tests should document that choice.

Implementation checkpoint:

- `DEFAULT_MIRROR_DIR` is the English default for new installs.
- `DEFAULT_ESPELHO_DIR` was removed during compatibility cleanup.
- The migration rehearsal tool follows the same directory policy without
  importing runtime config or triggering database copy side effects.
- The production data directory is not moved automatically. Existing
  `~/.espelho` installs require an explicit operational move or explicit
  environment configuration before using the English-only runtime.

Primary files:

- `src/memory/config.py`
- `.env.example`
- path/config tests

### 5. Active Python Internals

Once persisted schema speaks English, rename internals to match.

Target changes:

- variables `travessia` -> `journey`
- variables `travessia_id` -> `journey_id`
- methods such as `get_memories_by_travessia` -> `get_memories_by_journey`
- task parsing helpers such as `parse_caminho_tasks` ->
  `parse_journey_path_tasks`
- comments and docstrings in active code

Primary files:

- `src/memory/client.py`
- `src/memory/services/`
- `src/memory/storage/`
- `src/memory/hooks/`
- `src/memory/intelligence/`
- `src/memory/cli/`

Implementation checkpoint:

- Active services and store methods use English `journey`/`journey_id` naming
  internally.
- Compatibility wrappers and aliases such as `travessia`, `travessia_id`,
  `get_caminho`, and `parse_caminho_tasks` were removed during compatibility
  cleanup.
- Task parsing now has the English primary helper
  `parse_journey_path_tasks`.
- New imported journey-path tasks use source `journey_path`.

### 6. CLI, Claude Skills, And Commands

Move user-facing command vocabulary to English.

Target changes:

- `--travessia` -> `--journey`
- `--travessia-id` -> `--journey-id`
- `--caminho` -> `--journey-path` where applicable
- `espelho` references -> `mirror`
- update `.claude/skills/mm:*`
- update command docs and examples

Compatibility behavior during the migration:

- Prefer hidden deprecated aliases if parser support is simple.
- Otherwise remove old flags in a dedicated breaking-change commit with tests
  that assert the new vocabulary.

Implementation checkpoint:

- Active CLI and Claude skill commands accept English `journey` vocabulary only.
- Portuguese CLI aliases were removed in the compatibility cleanup checkpoint.

Primary files:

- `.claude/skills/mm:*/`
- `src/memory/cli/`
- `CLAUDE.md`
- CLI tests

### 7. Documentation

Update active documentation and skill text after behavior changes.

Final language goal:

- All active project docs and all active `.claude/skills/mm:*` text should be
  English.
- There should be no Portuguese text left in active documentation, command
  examples, user-facing copy, comments, or skill instructions unless it is
  intentionally documenting a legacy compatibility alias during the transition.
- Historical session logs, migration history, and compatibility tests may keep
  Portuguese terms when they are describing past behavior or asserting legacy
  support.

Target files:

- `README.md`
- `REFERENCE.md`
- `CLAUDE.md`
- `.env.example`
- `NEXT_SESSION_HANDOFF.md`
- `docs/portuguese-domain-language-inventory.md`
- `.claude/skills/mm:*/SKILL.md`

Rules:

- Current docs should use English domain language.
- Compatibility notes may mention old names.
- Historical session logs should remain historical.

### 8. Compatibility Removal

Remove Portuguese compatibility only after the English migration is verified.

Completed removals:

- `src/memoria/`
- `memory.services.travessia`
- `TravessiaService`
- Portuguese `MemoryClient` attributes and wrappers
- Portuguese keyword aliases such as `travessia=`
- Portuguese CLI aliases
- runtime legacy data fallbacks for `travessia`, `caminho`, and `.espelho`

Migration-only support remains in the rehearsal/migration tooling and tests so
old databases can still be validated and migrated forward deliberately.

## Proposed Commit Sequence

1. `Document English domain migration plan`
2. `Add tests for English schema migration`
3. `Migrate database schema from travessia to journey`
4. `Migrate identity data to English journey keys`
5. `Rename mirror filesystem configuration`
6. `Rename internal journey path terminology`
7. `Update commands and skills to English vocabulary`
8. `Update public docs for English domain language`
9. `Remove Portuguese compatibility APIs`
10. `Remove Portuguese CLI compatibility aliases`
11. `Remove runtime legacy data compatibility`
12. `Refresh final migration handoff and test naming`
13. `Validate English-only runtime operationally`

The exact split can change if tests reveal a safer boundary.

## Implementation Status

Completed:

- Characterization and migration tests for the English schema/data transition.
- SQLite schema migration from `travessia`/`travessia_id` to
  `journey`/`journey_id`.
- Identity layer and YAML migration from `travessia`/`caminho` to
  `journey`/`journey_path`.
- Default local storage rename from `.espelho` to `.mirror-poc`.
- Internal journey path terminology cleanup in the active implementation.
- CLI and Claude skill workflow update to English-only `journey` vocabulary.
- Public docs and handoff updated to English domain language.
- Portuguese Python compatibility APIs, CLI aliases, runtime identity fallbacks,
  and legacy storage discovery removed.
- English-only runtime smoke validated against an isolated temporary memory
  home:
  - seeded identity into a test database
  - listed journeys through `python -m memory list journeys`
  - loaded mirror context with `--journey mirror-poc`
  - wrote mirror state with `journey` and no `travessia`
  - added/listed a task scoped to `journey="mirror-poc"`
  - added/searched a memory scoped to `journey="mirror-poc"`
  - confirmed `.mirror-poc` was created and `.espelho` was not

Next:

- Move back to product work. Keep Portuguese term searches as a regression
  check when touching migration-sensitive areas.

## Verification Gates

Run after each implementation commit:

```text
pytest
ruff check src/ tests/
ruff format --check src/ tests/
```

Run after typed API or model changes:

```text
pyright src/memory
```

Run before declaring the migration complete:

```text
rg "travessia|caminho|espelho|memoria|conversa|tarefa|anexo|identidade"
```

Expected final search results:

- historical session logs
- migration notes
- migration/rehearsal tests for old-name data migration
- no active English-first implementation references unless intentionally
  testing old-name migration

## Rollback Strategy

The tag `pre-english-domain-migration` marks the stable point before risky
migration work.

For code rollback:

- use Git to inspect or revert individual migration commits
- avoid broad destructive reset operations while local data migration is being
  tested

For data rollback:

- database migration tests should create temporary databases
- production-like migration should require a backup before applying schema
  changes
- filesystem migration should copy before deleting or renaming old state

## Definition Of Done

The full migration is done when:

- fresh databases are created with English schema names
- old databases migrate to English schema names without losing data
- active identity data uses English paths and keys
- local filesystem configuration uses English mirror terminology
- active Python internals use English domain names
- CLI and Claude skill workflows use English arguments and docs
- public docs show English-first usage
- tests, Ruff, formatting, and Pyright pass
- repository-wide Portuguese term search has only intentional historical or
  migration references
- isolated runtime smoke test passes without creating `.espelho`
