[< CV3.E4 Skill Architecture Cleanup](../index.md)

# CV3.E4.S1 — SKILL.md Dispatch Fixes

**Story:** Fix stale dispatch paths — no Python changes  
**Status:** —

---

## What This Is

Five skills have dispatch commands that bypass the stable `python -m memory <command>`
interface: old-style `python3 -m memory.cli.*` paths, or calls to sibling run.py files.
This story fixes them with SKILL.md edits only — no Python code changes.

---

## Files to Change

### Claude: mm:backup/SKILL.md

```diff
- python3 -m memory.cli.backup
+ python -m memory backup
```

### Claude: mm:mute/SKILL.md

```diff
- python3 -m memory.cli.conversation_logger status
+ python -m memory conversation-logger status

- python3 -m memory.cli.conversation_logger mute
+ python -m memory conversation-logger mute

- python3 -m memory.cli.conversation_logger unmute
+ python -m memory conversation-logger unmute
```

### Claude: mm:new/SKILL.md

```diff
- python3 -m memory.cli.conversation_logger switch
- python3 .claude/skills/mm:mirror/run.py deactivate
+ python -m memory conversation-logger switch
+ python -m memory mirror deactivate
```

### Claude: mm:review-copy/SKILL.md

```diff
- python3 .claude/skills/mm:consult/run.py FAMILY TIER "PROMPT" \
+ python -m memory consult FAMILY TIER "PROMPT" \
```

### Pi: mm-review-copy/SKILL.md

```diff
- python3 .pi/skills/mm-consult/run.py FAMILY TIER "PROMPT" \
+ python -m memory consult FAMILY TIER "PROMPT" \
```

---

## Done Condition

- All five SKILL.md files updated
- No `python3 -m memory.cli.*` references remain in any SKILL.md
- No SKILL.md references any `run.py` file in another skill directory
- Tests pass
