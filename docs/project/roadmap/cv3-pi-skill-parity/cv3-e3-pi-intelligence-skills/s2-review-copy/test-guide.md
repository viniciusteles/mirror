[< S2 Plan](plan.md)

# CV3.E3.S2 — Test Guide

> Retrospective note: later CV6 work reclassifies `mm-review-copy` as a
> reference extension example rather than a permanent core framework feature.
> This does not change what CV3 needed to verify at the time.

## Automated Tests

No automated tests — this skill is model-driven. Verify by inspection only.

## Manual Verification

### 1. Skill directory exists

```bash
ls .pi/skills/mm-review-copy/
# Expected: SKILL.md
```

### 2. SKILL.md references Pi dispatch

```bash
grep "mm-consult" .pi/skills/mm-review-copy/SKILL.md
# Expected: python3 .pi/skills/mm-consult/run.py
```

### 3. No Claude Code paths in Pi SKILL.md

```bash
grep ".claude" .pi/skills/mm-review-copy/SKILL.md
# Expected: no output
```

### 4. Full suite still passes

```bash
python -m pytest tests/ -x -q
```
