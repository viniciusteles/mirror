[< Process](../index.md#process)

# Troubleshooting

Operational issues that have been diagnosed in the wild, with their root causes
and the fixes that addressed them. The goal is twofold: help future users (and
future us) recognize symptoms quickly, and preserve the reasoning behind each
fix so we don't re-debug the same class of problem.

When you resolve a non-trivial bug, add an entry here. Keep entries scoped to
the smallest reproducible cause. Open problems that have a known workaround
but no fix yet are also welcome (mark them `Status: mitigated`).

---

## Contents

- [Pi logger fails silently when `python3` resolves outside the project venv](#pi-logger-fails-silently-when-python3-resolves-outside-the-project-venv)

---

## Pi logger fails silently when `python3` resolves outside the project venv

**Date:** 2026-05-10
**Status:** resolved
**Affected component:** `.pi/extensions/mirror-logger.ts`
**Severity:** silent data-pipeline loss (no conversations or messages persisted to the database during affected sessions)

### Symptom

The Pi runtime appears to work normally. `mm-mirror`, `mm-journeys`, and other
skills run fine. But the conversation history is never persisted:

- `uv run python -m memory conversations --limit 10` shows no rows from the current Pi session
- `runtime_sessions` table is empty (no row with `active = 1` for the current session)
- `mm-recall`, `mm-conversations`, and any feature that depends on the message history return as if the session never happened

The only visible signal that something is wrong is buried in
`~/.mirror/mirror-logger.log`, which accumulates lines like:

```
2026-05-10T23:22:26.518Z [WARN] stderr from [-m memory conversation-logger]:
/Users/alissonvale/.pyenv/versions/3.10.6/bin/python3: No module named memory
```

These appear on **every turn** but never surface to the user because the
extension is designed to swallow failures to avoid blocking Pi.

### Diagnosis

Three checks confirm the issue:

1. Tail the extension log:
   ```bash
   tail -50 ~/.mirror/mirror-logger.log
   ```
   If you see repeated `No module named memory` warnings, you are hitting this bug.

2. Confirm the path of `python3`:
   ```bash
   which python3
   python3 -c "import memory"
   ```
   The first command will usually point at a pyenv shim or a system Python. The
   second will fail with `ModuleNotFoundError`.

3. Confirm the project venv has the package:
   ```bash
   .venv/bin/python -c "import memory; print(memory.__file__)"
   ```
   This should succeed and print the path inside `.venv/lib/.../site-packages`.

If the first two checks indicate `python3` resolves outside the venv but the
third works, you are hitting the bug.

### Root cause

The Pi extension at `.pi/extensions/mirror-logger.ts` invokes the Python CLI
on every conversation turn:

```typescript
const result = await pi.exec("python3", args, { timeout: 30_000 });
```

`pi.exec("python3", ...)` resolves `python3` via the user's `PATH`. On a
machine with pyenv (or any user-level Python manager) ahead of the project
venv in `PATH`, this picks up a Python that does not have the project's
dependencies installed. The `memory` package lives in `.venv/lib/.../site-packages`,
which is only on `sys.path` when the venv interpreter is used.

The extension was specifically designed to **fail silently** (see the
`try/catch` around the exec call and the comment in `runPy`) so that any
failure in the persistence pipeline does not block the user's Pi session.
That design choice is correct for usability, but it also means a bug at this
layer can persist for a long time without any visible signal.

### Fix

Replace `python3` with `uv run python` so the project venv is used regardless
of `PATH` order. This aligns with the project convention (`AGENTS.md`: "Use
`uv run` for project Python commands") and works without requiring any
filesystem-relative path resolution because `uv` discovers the venv from the
process `cwd`.

```typescript
// .pi/extensions/mirror-logger.ts (line ~75)
const result = await pi.exec("uv", ["run", "python", ...args], {
    timeout: 30_000,
});
```

After saving the file, the fix takes effect on the next Pi session. Existing
in-flight sessions still hold the old extension code in memory and continue
to fail until restarted.

### Recovery of affected sessions

The Pi runtime persists each turn to its own session file on disk (independent
of the database). Even when the extension's database push fails, the Pi
session file preserves every user and assistant message. The `session-start`
sub-command of `conversation-logger` scans for orphaned Pi session files and
backfills them into the database.

Run after restarting Pi (or manually any time):

```bash
uv run python -m memory conversation-logger session-start
```

The output reports how many orphaned sessions were ingested. The most recent
incident backfilled 15 sessions accumulated over roughly a month, with no
data loss.

### Prevention

Three avenues are worth considering:

1. **Surface persistence failures.** The current design swallows errors to
   keep Pi responsive. Consider adding a visible indicator (e.g. a one-line
   note in `mm-mirror` output or a status check on `mm-help`) when
   `~/.mirror/mirror-logger.log` shows recent `WARN`/`ERROR` lines.
2. **Document the convention.** The project already mandates `uv run` for
   Python invocations. Any new Pi extension should follow the same rule;
   it is worth calling this out explicitly in the extension author guide
   when one exists.
3. **Periodic backfill.** Even with the fix in place, running
   `conversation-logger session-start` opportunistically catches any future
   regressions before they accumulate.

---

<!-- New entries go above this line. Keep the most recent first. -->
