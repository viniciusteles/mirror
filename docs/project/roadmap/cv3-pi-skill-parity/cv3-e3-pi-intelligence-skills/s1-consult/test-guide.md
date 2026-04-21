[< S1 Plan](plan.md)

# CV3.E3.S1 — Test Guide

## Automated Tests

No unit tests for this story — `cmd_ask` and `cmd_credits` make live network
calls to OpenRouter. Integration tests for the CLI wiring use the existing
pattern: verify the module is importable and `main` is callable.

Run the full suite to confirm nothing regressed:

```bash
python -m pytest tests/ -x -q
```

## Manual Smoke Tests

### 1. Credits (no network I/O beyond OpenRouter balance check)

```bash
python -m memory consult credits
```

Expected: balance bar with `R$` amount printed.

### 2. Ask via CLI dispatch

```bash
python -m memory consult gemini lite "What is 2+2?"
```

Expected: response printed between `--- response via ... ---` and `--- end ---`,
followed by token counts and call cost.

### 3. Claude Code skill still works

```bash
python3 .claude/skills/mm:consult/run.py credits
```

Expected: same output as above (thin wrapper calls the same `main()`).

### 4. Pi skill wrapper

```bash
python3 .pi/skills/mm-consult/run.py credits
```

Expected: same output.

### 5. Error paths

```bash
python -m memory consult
# Expected: usage printed, exit 1

python -m memory consult gemini
# Expected: "Error: question is required." printed, exit 1
```
