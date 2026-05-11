# Testing Guide

This document defines the testing standard for the extension system and for
extensions themselves. The mirror project follows TDD for behavior changes;
the same expectation applies to extensions.

## Two scopes

Tests live in two places:

- **Core tests** — under `tests/extensions/` in the mirror repo. They cover
  the extension system: loader, API, migrations runner, binding registry,
  Mirror Mode hook. These tests use fixture extensions that do nothing
  interesting, just exercise the contract.
- **Extension tests** — under `<extension-root>/tests/` in the extension's
  own repo. They cover the extension's own behavior: schema, importers,
  reports, context providers. These tests run against the real
  `ExtensionAPI` using an in-memory or temporary database.

This document covers both.

## Test database setup

Every test that touches the database creates a fresh SQLite file or uses
`:memory:`. Tests must not share state.

A small helper, exposed by the core as `memory.extensions.testing`:

```python
from memory.extensions.testing import api_for_test

def test_something():
    with api_for_test(extension_id="hello", migrations_dir=...) as api:
        api.execute("INSERT INTO ext_hello_pings (message, created_at) VALUES (?, ?)",
                    ("test", "2026-05-10T00:00:00Z"))
        rows = api.read("SELECT count(*) AS c FROM ext_hello_pings").fetchone()
        assert rows["c"] == 1
```

`api_for_test`:

- creates a fresh SQLite database,
- applies the core schema (the bits the API depends on, like
  `_ext_migrations` and `_ext_bindings`),
- runs the extension's migrations,
- yields a real `ExtensionAPI` scoped to the given extension id.

The helper is provided by the core because extensions should never have to
reverse-engineer the API construction.

## Standard test layers

### Layer 1 — Schema and migrations

For each migration, write a test that:

1. Starts from the schema state *before* the migration.
2. Applies the migration.
3. Asserts the resulting schema (tables, columns, indices).
4. If data migration is part of the file, seeds representative rows in step
   1 and asserts their final state in step 3.

```python
def test_migration_002_adds_balance_after():
    with api_for_test(extension_id="finances", migrations_dir=migrations_through(1)) as api:
        # state before 002
        api.execute("INSERT INTO ext_finances_transactions (...) VALUES (...)")
    with api_for_test(extension_id="finances", migrations_dir=migrations_through(2)) as api:
        # state after 002
        cols = [r["name"] for r in api.read("PRAGMA table_info(ext_finances_transactions)")]
        assert "balance_after" in cols
```

### Layer 2 — Store / repository

Pure CRUD tests. Insert, read back, update, delete. No business logic. Each
test is a single behavior.

### Layer 3 — Services and reports

Tests that compose store operations into business logic: import flows,
report generators, search. These tests seed a small fixture of rows, run
the function, and assert the structured output.

### Layer 4 — CLI subcommands

Invoke the registered handler with arguments, capture stdout/stderr, assert
exit code and output shape.

```python
def test_cli_runway(capsys):
    with api_for_test(extension_id="finances", migrations_dir=...) as api:
        register(api)
        seed_some_accounts(api)
        rc = api._cli_registry["runway"](api, [])
        assert rc == 0
        out = capsys.readouterr().out
        assert "runway" in out.lower()
```

### Layer 5 — Mirror Mode hook

Tests that:

1. Install a fixture extension.
2. Bind one of its capabilities to a persona.
3. Trigger `load_mirror_context(persona=<persona>)` and assert the
   provider's output appears in the prompt.

These tests live in the core repo because they cross the boundary between
core and extension. The fixture extension is minimal (`ext-hello`).

## Edge cases every extension should cover

- **Empty database.** Every command must succeed (with empty output) when
  no rows exist.
- **Missing related rows.** Reading a foreign-key target that does not
  exist (account deleted but transaction remains) should not crash.
- **Bad input.** CLI handlers should print a helpful error and return a
  non-zero exit code, not raise.
- **Idempotent imports.** Importers should dedupe by a stable id and
  produce the same final state on re-run.
- **UTF-8 and Latin-1.** Files from external systems often come in
  Latin-1. Parsers should detect or be told.
- **Provider returning None.** Mirror Mode should handle a `None` return
  without warning.
- **Provider raising.** Mirror Mode should catch the exception, log it,
  and continue assembling the rest of the prompt.

## Conventions

- **One assertion per concept.** Multiple `assert` lines are fine if they
  describe the same outcome; split tests when they describe different
  outcomes.
- **Fixtures small and inline.** Most tests do not need shared fixtures.
  Inline seed data is easier to read than `conftest.py` machinery.
- **Names describe behavior, not implementation.** `test_runway_uses_bills_when_available`,
  not `test_runway_calls_monthly_burn_from_bills`.
- **Run in CI.** Every extension should have a CI workflow that runs its
  tests against the latest mirror release. Core tests run on every push to
  the mirror repo.

## Running tests

Inside the mirror repo:

```bash
uv run pytest tests/extensions/
```

Inside an extension repo:

```bash
uv run pytest tests/
# or, if the extension declares its own pyproject:
pytest tests/
```

Extensions should pin a compatible version of the mirror in their
`pyproject.toml` for reproducibility.

## What is intentionally not tested

- **Real LLM and embedding calls.** Always mocked. Both `api.llm` and
  `api.embed` accept a test mode that returns fixed strings / fixed
  vectors. Hitting real APIs in CI is wasteful and flaky.
- **Network resources.** Extensions that talk to external services (banks,
  CRMs) should mock at the boundary, not at the API level.
- **Sleep and timing.** Time-dependent code uses an injectable clock.
