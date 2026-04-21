# Portuguese Domain Language Inventory

Date: 2026-04-16

## Purpose

This inventory maps the remaining Portuguese domain language after the
English-first Python API cleanup. Its purpose is to separate low-risk code
renames from higher-risk product, persisted data, identity, command, and
filesystem decisions.

This is a decision aid, not a migration plan. It intentionally does not propose
renaming schema columns, data files, command names, or product concepts until
the desired domain language is explicit.

## Current Boundary

The active Python package is now English-first:

- `memory.*` is the primary package.
- `MemoryClient` exposes English service attributes and methods.
- `memory.services.journey.JourneyService` is the primary journey service.
- English client keywords such as `journey=` and `journey_id=` are supported.

Portuguese names still exist for compatibility and because some names are
persisted or product-facing domain language:

- `memoria.*`
- `travessia`, `travessia_id`
- `caminho`
- `espelho`
- `conversa`
- `tarefa`
- `anexo`
- `identidade`

## Risk Summary

| Area | Risk | Why |
| --- | --- | --- |
| Persisted SQLite schema and migrations | High | Renaming requires data migration, compatibility reads, index handling, and tests against existing databases. |
| Identity YAML and seeded identity layers | High | Keys and layer names can affect loaded identity context and existing identity files. |
| Filesystem paths and local state | High | Users may already have data under `~/.espelho`, `memoria*.db`, or exported `conversas/` paths. |
| Claude slash commands and skill inputs | Medium to high | Commands are user-facing workflow contracts, not just code symbols. |
| Python compatibility API | Medium | Existing callers may import `memoria.*`, `TravessiaService`, or Portuguese client wrappers. |
| Internal Python implementation names | Low to medium | Many are now compatibility wrappers, but some mirror persisted fields and should not be renamed casually. |
| Tests and documentation | Low to medium | Mostly mechanical, but tests also encode compatibility and product-language decisions. |

## Persisted Schema And Storage

Risk: high.

Primary files:

- `src/memory/db/schema.py`
- `src/memory/db/migrations.py`
- `src/memory/models.py`
- `src/memory/storage/store.py`

Remaining Portuguese terms include:

- `conversations.travessia`
- `memories.travessia`
- `tasks.travessia`
- `attachments.travessia_id`
- indexes such as `idx_memories_travessia`, `idx_tasks_travessia`,
  `idx_attachments_travessia`
- migration naming such as `001_project_to_travessia`
- identity layer values documented as `travessia` and `caminho`
- dataclass fields such as `travessia` and `travessia_id`
- store methods such as `get_memories_by_travessia`

Why this is risky:

- These names are stored in SQLite databases.
- Old databases may already exist in developer or user environments.
- Store queries, model fields, migrations, and tests must move together.
- A simple rename would likely break existing data or compatibility imports.

Decision needed:

- Keep persisted names as Portuguese indefinitely, or migrate them to English
  with an explicit compatibility and data migration plan.

## Identity Data And YAML

Risk: high.

Primary files and paths:

- `identity/travessias/*.yaml`
- `identity/personas/*.yaml`
- `identity/*.yaml`
- identity loading code under `src/memory/services/identity.py`

Remaining Portuguese terms include:

- directory name `identity/travessias`
- YAML key `travessia_id`
- identity layer concepts such as `travessia` and `caminho`
- domain content that intentionally uses terms such as `travessia`

Why this is risky:

- The identity files are project data, not merely implementation code.
- The terms may be meaningful product language rather than accidental
  Portuguese leftovers.
- Changing keys without compatibility would break loading existing identity
  files.

Decision needed:

- Decide whether `travessia` and `caminho` remain intentional identity/product
  concepts, or whether they become `journey` and a new English equivalent for
  `caminho`.

## Filesystem And Operational State

Risk: high.

Primary files:

- `src/memory/config.py`
- `.env.example`
- `.gitignore`
- migration and database path tests

Remaining Portuguese terms include:

- default directory `~/.espelho`
- config name `DEFAULT_ESPELHO_DIR`
- legacy database names such as `memoria.db` and `memoria_test.db`
- ignored export/work directories such as `conversas/`

Why this is risky:

- These paths may already contain local data.
- Renaming the default directory changes where the application looks for user
  state.
- Database renames need fallback discovery, copy or move rules, and clear
  deprecation behavior.

Decision needed:

- Keep `~/.espelho` as the durable product storage location, or introduce a new
  English path with backwards-compatible discovery.

## Python Compatibility API

Risk: medium.

Primary files and paths:

- `src/memoria/`
- `src/memory/client.py`
- `src/memory/services/travessia.py`
- `src/memory/services/__init__.py`
- `src/memoria/services/__init__.py`

Remaining Portuguese terms include:

- compatibility package `memoria.*`
- compatibility classes such as `TravessiaService`
- compatibility client attributes such as `travessias`, `tarefas`,
  `conversas`, `anexos`, and `identidade`
- compatibility methods such as `load_espelho_context`,
  `get_caminho`, `set_caminho`, `detect_travessia`,
  and `import_from_caminho`

Why this is risky:

- This is public or semi-public Python API surface.
- Existing code may still import Portuguese names.
- Removing compatibility before users migrate would be a breaking change.

Decision needed:

- Choose a support policy for Portuguese compatibility APIs: permanent aliases,
  documented deprecation, or removal in a later breaking version.

## Active Python Internals

Risk: low to medium.

Primary files:

- `src/memory/services/journey.py`
- `src/memory/services/tasks.py`
- `src/memory/services/conversation.py`
- `src/memory/hooks/*.py`
- `src/memory/intelligence/*.py`

Remaining Portuguese terms include:

- internal variables that mirror persisted fields, especially `travessia`
- task parsing names such as `parse_caminho_tasks`
- identity and journey logic that still passes `travessia` and `caminho` to the
  storage layer

Why this is risky:

- Some internal names can be cleaned up safely.
- Others intentionally match persisted schema fields and should stay aligned
  until the storage model changes.

Decision needed:

- Only rename internals where they do not obscure the persisted field mapping.
  Otherwise, keep the Portuguese storage boundary explicit.

## CLI, Claude Skills, And Commands

Risk: medium to high.

Primary files and paths:

- `.claude/skills/mm:*/`
- `CLAUDE.md`
- `README.md`
- `REFERENCE.md`
- `src/memory/cli/`

Remaining Portuguese terms include:

- command arguments such as `--travessia`
- skill and docs language around `travessia`, `caminho`, `espelho`,
  `conversa`, and `tarefa`
- slash command names and command documentation, including `/mm:*` workflows

Why this is risky:

- Commands and docs are user-facing contracts.
- Renaming them changes the workflow vocabulary, not only implementation names.
- Some English command names already exist while their arguments still expose
  Portuguese domain terms.

Decision needed:

- Decide whether the user-facing product language remains bilingual or moves to
  fully English command vocabulary.

## Documentation

Risk: medium.

Primary files:

- `README.md`
- `REFERENCE.md`
- `CLAUDE.md`
- `NEXT_SESSION_HANDOFF.md`
- `docs/session-logs/`

Remaining Portuguese terms include:

- historical discussion of `memoria`
- product vocabulary such as `espelho`, `travessia`, and `caminho`
- API examples that may still show Portuguese names

Why this is risky:

- Some references are historical or compatibility notes and should not be
  erased.
- Other references may now be stale after the English API cleanup.

Decision needed:

- Separate current public documentation from historical session logs and
  compatibility notes.

## Tests

Risk: low to medium.

Primary files:

- `tests/unit/memory/`
- `tests/integration/memory/`
- migration and storage tests

Remaining Portuguese terms include:

- compatibility API assertions
- persisted schema expectations
- fixture data that uses `travessia`, `caminho`, and `espelho`

Why this is risky:

- Tests should continue to protect compatibility names where they are
  intentional.
- Tests should change only when the supported behavior changes.

Decision needed:

- Keep compatibility tests while Portuguese APIs are supported.
- Add migration tests before any persisted rename.

## Term-Level Notes

`travessia`

- Current English API equivalent: `journey`.
- Still appears in persisted schema, identity data, compatibility APIs, tests,
  docs, and command arguments.
- Highest-impact remaining term.

`caminho`

- Current English API equivalent is less settled. Existing code uses
  journey path naming at the client boundary.
- Still appears in identity layers, task import logic, docs, and compatibility
  methods.
- Needs a product-language decision before a broad rename.

`espelho`

- Current English API equivalent: `mirror`.
- Still appears in the default storage path `~/.espelho`, config names, docs,
  and compatibility methods.
- Filesystem migration makes this higher risk than a normal code rename.

`memoria`

- Current English API equivalent: `memory`.
- Mostly compatibility package and legacy database naming.
- Keep until there is a deliberate deprecation policy for old imports and local
  database discovery.

`conversa`, `tarefa`, `anexo`, `identidade`

- Current English equivalents: `conversation`, `task`, `attachment`,
  `identity`.
- Mostly compatibility API, docs, tests, and user-facing workflow language.
- Lower risk than `travessia`, `caminho`, and `espelho`, except where names are
  persisted or user-facing.

## Suggested Next Decisions

Option A: Keep Portuguese product concepts.

- Treat `travessia`, `caminho`, and `espelho` as intentional product language.
- Keep English Python API wrappers for developer ergonomics.
- Document the bilingual boundary explicitly.
- Avoid schema, identity, command, and filesystem migrations for now.

Option B: Migrate fully to English.

- Rename persisted fields, identity keys, command arguments, docs, and storage
  paths.
- Requires a design note and a staged migration plan before implementation.
- Highest consistency, highest migration cost.

Option C: Hybrid boundary.

- Keep the current English-first Python API.
- Preserve Portuguese persisted/product concepts until they become painful.
- Clean stale docs and internals around the boundary.
- Revisit persisted and command naming only after the product vocabulary is
  decided.

Recommendation: continue with Option C unless the product goal is explicitly to
remove Portuguese domain language everywhere. It preserves momentum while
keeping the risky migrations visible and deliberate.

## If Full Migration Is Chosen Later

A safe migration should probably be staged:

1. Write a short design note naming the target vocabulary.
2. Add read compatibility for both old and new names.
3. Add migration tests using an old-schema database fixture.
4. Migrate schema columns, indexes, models, and store methods together.
5. Migrate identity YAML keys with fallback loading for old files.
6. Add filesystem discovery for old and new storage locations.
7. Update commands, docs, and examples.
8. Deprecate Portuguese compatibility APIs only after callers have an English
   replacement.

