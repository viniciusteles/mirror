[CV14.E2](../index.md) › **S1 Install ignores `.git`/`__pycache__`/`.venv`**

# CV14.E2.S1 — Install ignores `.git`/`__pycache__`/`.venv`

**Status:** ✅ Done · 2026-05-11

## Problem

`memory.cli.extensions.install_extension` calls
`shutil.copytree(source_dir, target_extension_dir, dirs_exist_ok=True)` to
mirror the source directory into the user's installed-extensions tree.
That works for the synthetic fixture under `tests/.../ext-hello/`, but
the moment the source is a real Git checkout (which every shareable
extension is), `copytree` walks into `.git/` and tries to overwrite the
read-only pack files that Git keeps under `objects/pack/`. The second
install fails with a `PermissionError`; the workaround until now has
been to `uninstall` first.

`__pycache__/` and `.venv/` are not strictly read-only, but copying
them is pointless and produces noisy diffs in the installed tree.

## Plan

- Pass `ignore=shutil.ignore_patterns(...)` to `copytree` so the
  problematic directories are never traversed at all.
- The pattern list lives next to the call site; if a future need
  arises we change it in one place.
- Patterns to ignore: `.git`, `__pycache__`, `.venv`, `*.pyc`,
  `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `node_modules`,
  `.DS_Store`. All of them are either generated, environment-local,
  or version-control internals — none belongs in an installed
  extension.

## Test Guide

- Source dir contains a `.git/` with a read-only file inside
  → `install_extension` succeeds and the `.git/` directory is **not
  present** under the installed extension dir.
- Same source dir, second call to `install_extension`
  → still succeeds (no `PermissionError`).
- Source dir contains `__pycache__/foo.pyc` → not copied.
- Source dir contains an empty `.venv/` directory → not copied.

## Acceptance

- Tests pass.
- `cd ~/Code/mirror && uv run python -m memory extensions install finances --extensions-root ~/Code/mirror-extensions` succeeds twice in a row on a real Git checkout.
