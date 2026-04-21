[< CV3.E3 Pi Intelligence Skills](../index.md)

# CV3.E3.S2 — Add `mm-review-copy` Pi Skill

**Story:** Port mm:review-copy to Pi as a model-driven skill  
**Status:** In Progress

---

## What This Is

`mm:review-copy` on Claude Code is SKILL.md-only — there is no `run.py`.
The agent reads the file, sends it to each specified model via `mm:consult`,
and assembles an HTML report. On Pi, the exact same model-driven approach
applies, but the dispatch is through Pi's skill system.

From the later CV6 perspective, this capability is better understood as a
**reference extension example** rather than a permanent core framework feature.
CV3 still correctly recorded the Pi-parity work needed to make it available.

The Pi skill calls `python3 .pi/skills/mm-consult/run.py` (not the Claude Code
variant), and saves output to `~/Downloads/`.

---

## Implementation Plan

### Step 1 — Create `.pi/skills/mm-review-copy/SKILL.md`

Adapted from `.claude/skills/mm:review-copy/SKILL.md`:
- Replace all references to `.claude/skills/mm:consult/run.py` with
  `python3 .pi/skills/mm-consult/run.py`
- Keep the HTML template and workflow identical

No `run.py` needed — the skill is agent-orchestrated.

---

## Files Changed

| File | Action |
|------|--------|
| `.pi/skills/mm-review-copy/SKILL.md` | New — model-driven, calls mm-consult |
