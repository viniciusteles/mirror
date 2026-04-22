[< S1 Index](index.md)

# Test Guide — CV1.E1.S1

## 1. Unit tests

```bash
pytest tests/unit/memory/skills/ -v
```

Expected: 9 tests pass.

---

## 2. Existing skill still works

```bash
python3 .claude/skills/mm:mirror/run.py load --journey mirror --context-only
```

Expected: identity context printed to stdout. No errors.

```bash
python3 .claude/skills/mm:mirror/run.py deactivate
```

Expected: "Mirror Mode deactivated." printed to stderr.

```bash
python3 .claude/skills/mm:mirror/run.py journeys
```

Expected: list of active journeys printed.

---

## 3. Full suite

```bash
pytest
ruff check src/ tests/
ruff format --check src/ tests/
pyright src/memory
git diff --check
```

Expected: all pass, no new failures.

---

## 4. State file integrity

```bash
python3 .claude/skills/mm:mirror/run.py load --journey mirror --context-only
cat ~/.mirror/mirror_state.json
```

Expected: JSON with `"active": true` and `"journey": "mirror"`.

```bash
python3 .claude/skills/mm:mirror/run.py deactivate
cat ~/.mirror/mirror_state.json
```

Expected: JSON with `"active": false`.
