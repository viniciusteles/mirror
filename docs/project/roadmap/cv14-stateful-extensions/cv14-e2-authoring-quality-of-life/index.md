[CV14](../index.md) › **E2 Authoring quality of life**

# CV14.E2 — Authoring quality of life

**Status:** ✅ Done · 2026-05-11
**Goal:** Smooth the three rough edges that surfaced while writing the first two real `command-skill` extensions (`finances`, `testimonials`) outside the mirror tree. Each story is a focused infrastructure fix that lets extension authors work without manual workarounds.

---

## Why now

[CV14.E1](../cv14-e1-command-skill-infrastructure/index.md) shipped the contract and proved it end-to-end with a synthetic `ext-hello` fixture. The two real extensions that followed (built in a separate repository) exposed three pain points the synthetic fixture never hit:

1. **`extensions install` chokes on `.git/`**. Real extensions live in real Git repos. Re-installing fails with `PermissionError` on Git's read-only pack files because `shutil.copytree` walks the entire source tree blindly.
2. **The loader does not add the extension directory to `sys.path`**. Every non-trivial extension that splits code into `src/` modules has to prepend a manual 4-line prelude to `extension.py`. Tedious and error-prone.
3. **Comment-only edits to applied migrations trigger the checksum guard with no escape hatch**. The guard is correct in spirit (never silently re-run a changed DDL), but the current implementation hashes the raw file, so adding a SQL comment to an already-applied migration is reported as drift. The author has to either revert the comment or edit `_ext_migrations` by hand.

None of these blocks an extension from being written, but every one of them produces a workaround that future authors will copy. Better to fix them once.

---

## Stories

| Code | Story | What changes | Status |
|------|-------|--------------|--------|
| [S1](cv14-e2-s1-install-ignores-git-tree/index.md) | Install ignores `.git`/`__pycache__`/`.venv` | `shutil.copytree(ignore=...)` so re-installs from a real Git checkout work | ✅ Done |
| [S2](cv14-e2-s2-loader-adds-sys-path/index.md) | Loader exposes extension root on `sys.path` | Extensions can `from src.foo import bar` with no prelude | ✅ Done |
| [S3](cv14-e2-s3-migration-checksum-ignores-comments/index.md) | Migration checksum is comment/whitespace-tolerant | Editing a comment in an applied migration no longer trips the drift guard | ✅ Done |

---

## Done Condition

- Each story shipped behind tests; CI green.
- A new extension can be `install`ed from a real Git checkout twice in a row with no errors.
- A command-skill that uses `from src.foo import bar` loads with no `sys.path` workaround.
- Adding or editing a `--` comment in an already-applied migration does not trip the checksum guard. Real structural edits still do.

---

## Out of Scope

- Doctor / lint / schema-dump tooling (these belong to a separate, optional E2 increment if real authoring pain ever surfaces them).
- Anything cross-extension (CV14.E3).
- Anything related to distribution (CV14.E4).

---

**See also:** [CV14 Stateful Extension System](../index.md) · [CV14.E1 Command-skill infrastructure](../cv14-e1-command-skill-infrastructure/index.md) · [Product · Extensions · Roadmap](../../../../product/extensions/roadmap.md)
