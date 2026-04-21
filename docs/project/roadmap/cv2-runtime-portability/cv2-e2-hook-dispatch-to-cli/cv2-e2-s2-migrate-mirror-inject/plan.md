[< CV2.E2 Hook Dispatch to CLI](../index.md)

# CV2.E2.S2 — Plan: Migrate mirror-inject.sh to CLI dispatch

## What and Why

`mirror-inject.sh` sets `RUN_PY` to the hardcoded skill script path and calls
it directly via `python3 "$RUN_PY" load ...`. This couples the hook to the
skill directory layout. It also exports `PYTHONPATH` to make the script
importable — unnecessary since `python -m memory` resolves the package without it.

The CLI command `python -m memory mirror load` is the stable interface and
already accepts all required flags. This story removes the hardcoded path and
drops the now-unnecessary `PYTHONPATH` export.

---

## Changes

**File:** `.claude/hooks/mirror-inject.sh`

**Remove:**
```bash
export PYTHONPATH="$CLAUDE_PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
...
RUN_PY="$CLAUDE_PROJECT_DIR/.claude/skills/mm:mirror/run.py"
```

**Case 1 — explicit /mm:mirror:**

Before:
```bash
CONTEXT=$(python3 "$RUN_PY" load --context-only --query "$QUERY" 2>/dev/null)
```

After:
```bash
CONTEXT=$(python3 -m memory mirror load --context-only --query "$QUERY" 2>/dev/null)
```

**Case 2 — auto-inject:**

Before:
```bash
ARGS=(load --context-only --query "$PROMPT")
[ -n "$PERSONA" ] && ARGS+=(--persona "$PERSONA")
[ -n "$JOURNEY" ] && ARGS+=(--journey "$JOURNEY")
CONTEXT=$(python3 "$RUN_PY" "${ARGS[@]}" 2>/dev/null)
```

After:
```bash
ARGS=(mirror load --context-only --query "$PROMPT")
[ -n "$PERSONA" ] && ARGS+=(--persona "$PERSONA")
[ -n "$JOURNEY" ] && ARGS+=(--journey "$JOURNEY")
CONTEXT=$(python3 -m memory "${ARGS[@]}" 2>/dev/null)
```

No Python code changes. Behavior is identical.

---

## Verification

```bash
# Case 1 — simulate /mm:mirror invocation
echo '{"message": "/mm:mirror what is my next priority"}' | bash .claude/hooks/mirror-inject.sh | head -3

# Case 2 — simulate active Mirror Mode (needs mirror_state to return true)
bash .claude/hooks/mirror-inject.sh < /dev/null
```

Neither call should produce a traceback. Output may be empty (Case 2 when Mirror Mode is not active) or identity context (when active).
