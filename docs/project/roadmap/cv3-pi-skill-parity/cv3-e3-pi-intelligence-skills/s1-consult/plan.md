[< CV3.E3 Pi Intelligence Skills](../index.md)

# CV3.E3.S1 — Add `consult` CLI command and Pi skill wrapper

**Story:** Port mm:consult to Pi via `python -m memory consult`  
**Status:** In Progress

---

## What This Is

`mm:consult` calls other LLMs through OpenRouter with Mirror identity context.
The logic lives in `.claude/skills/mm:consult/run.py`. This story extracts it
into a proper CLI module at `src/memory/cli/consult.py`, wires it into
`__main__.py`, and creates the Pi skill wrapper.

---

## Implementation Plan

### Step 1 — Create `src/memory/cli/consult.py`

Extract the logic from `.claude/skills/mm:consult/run.py` verbatim. The module
already has a clean `main()` function. No changes needed to the logic.

```python
# src/memory/cli/consult.py
# Extracted from .claude/skills/mm:consult/run.py
# parse_args(), cmd_ask(), cmd_credits(), main() — unchanged
```

### Step 2 — Wire into `src/memory/__main__.py`

Add `elif command == "consult":` branch following the established pattern:

```python
elif command == "consult":
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    from memory.cli.consult import main as _consult_main
    _consult_main()
```

Update the USAGE string to include `consult`.

### Step 3 — Update `.claude/skills/mm:consult/run.py`

Replace the self-contained implementation with a thin import:

```python
#!/usr/bin/env python3
"""Consult skill: ask other LLMs through OpenRouter."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from memory.cli.consult import main

if __name__ == "__main__":
    main()
```

This keeps Claude Code working while the canonical logic moves to the package.

### Step 4 — Create `.pi/skills/mm-consult/`

`SKILL.md`: mirrors `.claude/skills/mm:consult/SKILL.md`, adapted for Pi
(uses `python3 .pi/skills/mm-consult/run.py` instead of
`python3 .claude/skills/mm:consult/run.py`).

`run.py`: thin wrapper importing `memory.cli.consult.main`.

---

## Files Changed

| File | Action |
|------|--------|
| `src/memory/cli/consult.py` | New — extracted from mm:consult run.py |
| `src/memory/__main__.py` | Add consult branch + USAGE entry |
| `.claude/skills/mm:consult/run.py` | Replace with thin import |
| `.pi/skills/mm-consult/SKILL.md` | New |
| `.pi/skills/mm-consult/run.py` | New |
