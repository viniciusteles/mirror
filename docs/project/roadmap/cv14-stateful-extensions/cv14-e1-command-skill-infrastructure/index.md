[Roadmap](../../index.md) › [CV14](../index.md) › **E1 Command-Skill Infrastructure**

# CV14.E1 — Command-Skill Infrastructure

**Epic:** Authors can write, install, and run stateful extensions end to end
**Status:** ✅ Done

---

## What This Is

The base layer of the stateful extension system. Everything else in
[CV14](../index.md) (and every concrete extension a user might build) depends
on what this epic ships: the manifest contract, the API surface, the migration
runner, the loader, the CLI dispatcher, the binding registry, and the Mirror
Mode injection point.

When this epic is Done, a user can:

1. Create an extension repository on disk.
2. Declare a `skill.yaml` manifest with `kind: command-skill`.
3. Write SQL migrations under `migrations/` (any tables prefixed with
   `ext_<id>_*`).
4. Write `extension.py` with a `register(api)` function that registers CLI
   subcommands and Mirror Mode context providers.
5. Run `python -m memory extensions install <id> --extensions-root <path>` —
   the mirror copies the source, runs migrations, validates the entrypoint
   by calling `register(api)`, and creates the runtime SKILL.md surfaces.
6. Run `python -m memory ext <id> <subcommand>` to invoke the extension.
7. Bind capabilities to personas with
   `python -m memory ext <id> bind <capability> --persona <persona_id>`.
8. See the extension's context appear automatically in Mirror Mode prompts
   under `=== extension/<id>/<capability> ===` headers when the bound persona
   is active.

The mirror never ships extension code; everything an extension exposes flows
through the API surface defined by this epic.

---

## Done Condition

- The manifest validator enforces `kind: command-skill` shape:
  `entrypoint.module` required and resolved to an existing `.py` file,
  `table_prefix` derived from id (`ext_<underscored_id>_`) or validated when
  declared, `skill_file` accepted optionally so the agent can read a SKILL.md
  describing the extension.
- The migration runner applies `migrations/*.sql` in lexicographic order,
  enforces the prefix contract on every DDL/DML/CREATE INDEX, tracks applied
  files by SHA-256 checksum in `_ext_migrations`, refuses to skip a file
  whose checksum changed, and runs each file inside an explicit `SAVEPOINT`
  so failures roll back atomically (including DDL, which a plain
  `with conn:` does not undo in the sqlite3 module's default deferred mode).
- The `ExtensionAPI` exposes `execute`/`read`/`executemany` with prefix
  enforcement on writes, `transaction()` (SAVEPOINT-backed), `embed()` and
  `llm()` wrappers, `register_cli()` and `register_mirror_context()`,
  `run_migrations()`, structured `log()`, and a documented raw `db` escape
  hatch. Writes outside the prefix raise `ExtensionPermissionError`; reads
  may touch any table.
- The loader validates the manifest, imports the entrypoint module via
  `importlib.util` (no `sys.path` pollution; registered under
  `memory_ext.<id>.<module>`), calls `register(api)`, and caches the
  resulting API by absolute directory path. A `reload=True` flag forces a
  fresh load. Every failure mode (manifest invalid, missing `register`,
  import error, `register` raises) becomes `ExtensionLoadError` with the
  offending `extension_id` attached.
- The CLI dispatcher `python -m memory ext` supports: `list`,
  `<id> [--help]`, `<id> <subcommand> [args...]`, `<id> bind|unbind
  <capability> (--persona|--journey|--global)`, `<id> bindings`,
  `<id> migrate`. Honors `--mirror-home` with `MIRROR_HOME` / `MIRROR_USER`
  fallback.
- The binding registry stores rows in `_ext_bindings` (composite primary key
  allows multiple targets per capability; secondary index keeps the Mirror
  Mode lookup cheap). The context dispatcher
  (`memory.extensions.context.collect_extension_context`) returns
  `ContextSection`s in stable order; every failure path (uninstalled
  extension, load error, missing capability, provider raises, provider
  returns None) is logged and skipped silently.
- `IdentityService.load_mirror_context` calls the context dispatcher after
  the core sections are assembled and appends results under
  `=== extension/<id>/<capability> ===` headers. The integration is wrapped
  defensively so a broken extension subsystem cannot break Mirror Mode.
- `extensions install` for a `command-skill` runs migrations and validates
  `register(api)` as part of the install path itself. `extensions uninstall`
  sweeps orphan binding rows while preserving the extension's own data
  tables (`ext_<id>_*`) so user data is never lost on accidental
  uninstall.
- A fixture extension `ext-hello` under
  `tests/unit/memory/extensions/fixtures/` exercises the entire chain.
- The full test suite is green. CI is green on the post-implementation push.

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| [CV14.E1.S1](cv14-e1-s1-command-skill-infra/plan.md) | Command-skill infrastructure (manifest, migrations, API, loader, CLI dispatcher, binding registry, Mirror Mode hook, install path) | ✅ Done |

The [story plan](cv14-e1-s1-command-skill-infra/plan.md) and
[test guide](cv14-e1-s1-command-skill-infra/test-guide.md) both delegate to
the canonical user story under the product docs:
[US-00 — Command-Skill Infrastructure](../../../../product/extensions/user-stories/US-00-infra-de-command-skill.md).
The roadmap-side files exist as thin pointers so the project tracking and the
product specification stay in sync without duplicating the substance.

---

## Verification

- Full test suite: 1103 passed (95 new under `tests/unit/memory/extensions/`).
- `uv run ruff check src/ tests/` clean.
- Manual smoke test against the real user mirror home: install -> ping/list
  via CLI -> bind to a persona -> verify bindings -> uninstall -> confirm
  data tables preserved and bindings swept. Documented in PR #7.
- CI: green on Python 3.10 and 3.12 (run id 25668728695).

---

**See also:** [Roadmap](../../index.md) · [CV14](../index.md) · [CV14.E1.S1 Plan](cv14-e1-s1-command-skill-infra/plan.md) · [CV14.E1.S1 Test Guide](cv14-e1-s1-command-skill-infra/test-guide.md) · [Product · Extensions](../../../../product/extensions/index.md) · [PR #7](https://github.com/viniciusteles/mirror/pull/7)
