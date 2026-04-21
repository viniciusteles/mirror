[< Plan](plan.md)

# CV5.E3.S2 — Test Guide — Runtime Validation and Regression Coverage

## Standard Verification

```bash
pytest
ruff check src/ tests/
ruff format --check src/ tests/
pyright src/memory
git diff --check
```

## Targeted Assertions

- concurrent session creation preserves all session bindings
- concurrent startup against a fresh DB does not fail migration bookkeeping
- two sessions can hold independent mirror state at the same time
- roadmap/worklog/docs no longer claim CV5 is intelligence-depth work
