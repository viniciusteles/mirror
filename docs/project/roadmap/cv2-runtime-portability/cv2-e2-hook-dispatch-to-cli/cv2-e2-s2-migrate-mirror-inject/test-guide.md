[< CV2.E2.S2 Plan](plan.md)

# CV2.E2.S2 — Test Guide: Migrate mirror-inject.sh to CLI dispatch

## Scope

Shell script dispatch change only. No Python logic changes.
Tests cover:

1. `python -m memory mirror load` produces identity output (existing coverage)
2. The hook script exits cleanly in both cases (manual smoke)
3. Full suite passes unchanged

---

## Existing Tests to Run

```bash
pytest tests/ -k "mirror" -v
```

Must pass before and after the change.

---

## Manual Smoke Tests

**Case 1 — explicit /mm:mirror invocation:**

```bash
printf '{"message":"/mm:mirror what should I focus on"}' | bash .claude/hooks/mirror-inject.sh | head -5
```

Expected: identity context printed (starts with `⏺ Mirror Mode active` or `=== self/soul ===`). Exit 0.

**Case 2 — no active Mirror Mode (default path):**

```bash
printf '{"message":"hello"}' | bash .claude/hooks/mirror-inject.sh
echo "exit: $?"
```

Expected: no output (Mirror Mode not active), exit 0, no traceback.

**Confirm run.py is no longer referenced:**

```bash
grep -r "run.py" .claude/hooks/mirror-inject.sh
```

Expected: no matches.

---

## Full Verification Suite

```bash
pytest tests/ -x -q
ruff check src/ tests/
ruff format --check src/ tests/
pyright src/
git diff --check
```

All must pass clean.
