[< CV2 Runtime Portability](../index.md)

# CV2.E2 — Hook Dispatch to CLI

**Epic:** Claude Code hooks call the Python CLI, not script paths  
**Status:** ✅ Done  
**Parallel with:** CV2.E1

---

## What This Is

`mirror-inject.sh` currently locates and calls `.claude/skills/mm:mirror/run.py`
directly using a hardcoded path. This creates a tight coupling between the hook
and the skill directory layout.

The Pi extension dispatches everything through `python -m memory ...`. Claude
Code hooks should do the same. The Python CLI (`python -m memory mirror load`)
is the stable interface; skill script paths are an implementation detail that
should not appear in hooks.

This epic migrates `mirror-inject.sh` to call `python -m memory mirror load`
instead of the skill script, matching the dispatch pattern Pi already uses.

---

## Done Condition

- `mirror-inject.sh` calls `python -m memory mirror load [args]` and does not
  reference `.claude/skills/mm:mirror/run.py`
- The CLI command `python -m memory mirror load` accepts `--context-only`,
  `--query`, `--persona`, `--journey`, `--org` flags (already exists via `run.py`
  — verify and expose through CLI if not yet done)
- Behavior of mirror injection is unchanged from the user's perspective
- Existing tests pass

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV2.E2.S1 | Expose `mirror load` as a first-class `python -m memory mirror` CLI command | ✅ (already existed) |
| CV2.E2.S2 | Migrate `mirror-inject.sh` to call the CLI command | ✅ |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV2 Runtime Portability](../index.md) · [CV2.E1 Session Lifecycle Parity](../cv2-e1-session-lifecycle-parity/index.md)
