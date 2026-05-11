[CV14.E2](../index.md) › **S2 Loader exposes extension root on `sys.path`**

# CV14.E2.S2 — Loader exposes extension root on `sys.path`

**Status:** ✅ Done · 2026-05-11

## Problem

The current loader imports `extension.py` directly from its on-disk path
via `importlib.util.spec_from_file_location`. That works for a one-file
extension, but every non-trivial `command-skill` we have written so far
splits code into `src/`: `src/models.py`, `src/store.py`, `src/cli/...`,
etc. To make those imports resolve, every `extension.py` currently
starts with a manual prelude:

```python
import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
```

Four lines of boilerplate, easy to forget, never customised. The
framework can do this for the author.

## Plan

- In `memory.extensions.loader._import_extension_module`, before
  calling `spec.loader.exec_module(module)`, insert the extension
  directory at the front of `sys.path` (idempotent: only if not
  already present).
- Leave it on `sys.path` after import. The extension may import
  `src.*` lazily inside a CLI handler, not just at module-load
  time, and the cost of one extra entry on `sys.path` is negligible.
- Document the behaviour in `docs/product/extensions/authoring-guide.md`
  so future authors know they may use `from src.foo import bar` directly.
- Update both real extensions (`finances`, `testimonials`) to drop
  the prelude in a follow-up commit on their own repo — out of scope
  for this story but called out in the changelog.

## Test Guide

- Build a synthetic fixture (under `tests/.../`) with:
  - `extension.py` containing `from src.greet import hello` and
    a CLI handler that calls `hello()`.
  - `src/greet.py` defining `def hello() -> str: return "hi"`.
- `load_extension(fixture_dir, connection=...)` succeeds (no
  `ModuleNotFoundError`) and the CLI handler returns `"hi"`.
- Loading two extensions with sibling-named `src` packages does
  not cross-contaminate: each resolves its own `src.greet`.
  *(If Python's import system makes this impossible to guarantee
  without a per-extension namespace, the test asserts the current,
  documented behaviour — last-loaded wins — and the guide warns
  against shared module names.)*

## Acceptance

- Tests pass.
- A real extension can drop the 4-line prelude from `extension.py`
  and still install + dispatch correctly.
- Authoring guide updated.
