[< S2 Index](index.md)

# Test Guide — CV1.E1.S2

## 1. Unit tests

```bash
pytest tests/unit/memory/test_main.py -v
```

Expected: all existing tests pass plus 4 new tests.

---

## 2. Mirror commands via unified CLI

```bash
python -m memory mirror load --journey mirror --context-only
```

Expected: identity context printed to stdout. Same output as calling the Claude skill directly.

```bash
python -m memory mirror journeys
```

Expected: list of active journeys.

```bash
python -m memory mirror deactivate
```

Expected: deactivation message.

---

## 3. Conversation-logger commands via unified CLI

```bash
python -m memory conversation-logger status
```

Expected: `ACTIVE` or `MUTED`.

```bash
python -m memory conversation-logger mute && python -m memory conversation-logger status
python -m memory conversation-logger unmute && python -m memory conversation-logger status
```

Expected: `MUTED` then `ACTIVE`.

---

## 4. Unknown commands exit with error

```bash
python -m memory nosuchcommand; echo "exit: $?"
```

Expected: usage printed, exit code 1.

```bash
python -m memory mirror nosuchsubcommand; echo "exit: $?"
```

Expected: error printed, exit code nonzero.

---

## 5. Full suite

```bash
pytest
ruff check src/ tests/
ruff format --check src/ tests/
pyright src/memory
git diff --check
```

Expected: all pass. No regressions.
