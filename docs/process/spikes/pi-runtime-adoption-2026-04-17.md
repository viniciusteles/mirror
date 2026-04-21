[< Process](../development-guide.md)

# Spike: Pi Runtime Adoption

**Date:** 2026-04-17  
**What was inspected:** `~/dev/workspace/mirror-pi` (Henrique's Pi-adapted Mirror Mind)  
**Outcome:** Implementation plan for CV1 Pi Runtime

---

## Motivation

The `mirror-pi` journey exists because Claude Code is not always the right
runtime. Pi (`badlogic/pi-mono`) is a model-agnostic local agent that does not
require Claude Code. Making Mirror Mind run on Pi means the mirror is available
regardless of which AI runtime the user chooses.

The question this spike answered: what useful ideas does `mirror-pi` have, and
what should not be copied?

---

## What Was Inspected

The full `~/dev/workspace/mirror-pi` repository. Key files examined:

- `.pi/settings.json` — Pi skill command registration
- `.pi/extensions/mirror-logger.ts` — Pi lifecycle integration (session-start, log-user, log-assistant, session-end)
- `.pi/skills/*` — Pi skill scripts using hyphenated command names (`mm-mirror`, `mm-consult`, etc.)
- `memoria/conversation_logger.py` — Pi session handling: stale orphan closing, pending extraction, Pi JSONL backfill, `--interface pi`

---

## Key Learnings

**1. Do not port `mirror-pi` wholesale.**  
It is pre-English-migration. Package name is `memoria`, journeys are `travessias`,
database is in `~/.espelho/`. Porting it wholesale would undo CV0.

**2. The `.pi/` structure is the right model for interface separation.**  
`.pi/settings.json` + `.pi/extensions/mirror-logger.ts` + `.pi/skills/mm-*/` 
is a clean pattern. The extension stays thin (dispatches to Python, swallows
failures, never blocks Pi).

**3. Shared skill logic is the central design problem.**  
If skill scripts are duplicated between `.claude/skills/` and `.pi/skills/`,
they will drift. The solution is `src/memory/skills/` — shared Python modules
that both interfaces call. This is the E1 prerequisite.

**4. The Pi session lifecycle is richer than Claude's.**  
Pi needs `session-start` (unmuting, orphan closing, pending extraction) because
Pi sessions are file-based, not process-based. The conversation logger needs
explicit lifecycle events that Claude's hook system handles implicitly.

**5. Pi transcript JSONL differs from Claude's.**  
The parser must handle both shapes. The session ID in Pi may be a file path
rather than a UUID string. This must be explicit and tested.

**6. The mirror-logger extension should be thin.**  
Call Python. Swallow failures. Log diagnostics. Never block Pi if memory
logging fails. The logic lives in Python, not TypeScript.

**7. `MIRROR_USER_DIR` separation is a future concern.**  
`mirror-pi` separates framework from user data. That is a valid future design.
It is not a CV1 requirement. First get Pi running against current `identity/`
and current database.

---

## Decisions Made

1. **Don't port wholesale.** `mirror-poc` is the source of truth. `mirror-pi` is
   a reference for interface patterns.

2. **Extract shared skill modules first** (`src/memory/skills/`). Pi wrappers
   cannot be written until the shared modules exist. This is CV1.E1.

3. **Use `.pi/` hyphenated naming.** Pi commands: `mm-mirror`, `mm-journey`, etc.
   Claude commands: `mm:mirror`, `mm:journey`, etc. Both call the same Python core.

4. **Port the mirror-logger extension against the English runtime.** Replace
   `~/.espelho` → `~/.mirror-poc`, `memoria` → `memory`, `travessia` → `journey`.

---

## Recommended Implementation Sequence

1. Extract skill logic into `src/memory/skills/` (CV1.E1.S1)
2. Add unified `python -m memory` CLI commands (CV1.E1.S2)
3. Add `.pi/` skeleton with skill wrappers (CV1.E2.S1)
4. Port mirror-logger extension against English runtime (CV1.E2.S2)
5. Add Pi session lifecycle to conversation logger (CV1.E3.S1)
6. Add Pi JSONL backfill and stale orphan handling (CV1.E3.S2)
7. End-to-end smoke validation on real Pi hardware (CV1.E4.S1)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Session ID shape differs (Pi uses file path, not UUID) | Explicit field, tested from the start |
| Transcript JSONL format differs | Parser handles both shapes with clear failure mode |
| Skill naming conflict (colon vs. hyphen) | Kept separate by design; no shared namespace |
| Duplicated skill code drifts | Blocked by E1 prerequisite: shared modules must exist before wrappers |
| Production DB mutation during validation | Isolated `HOME`/`MEMORY_DIR` smoke test, same pattern as CV0 |

---

## Open Questions

- What is the Pi session file path format? (`~/.pi/agent/sessions/<id>/...`)  
  Verify against actual Pi runtime before writing the logger.
- Does Pi provide a session ID at startup, or must we derive one from the file path?  
  The `mirror-pi` spike stores file paths as session IDs — verify this is still the case.

---

**See also:** [CV1 Pi Runtime](../../project/roadmap/cv1-pi-runtime/index.md) · [Briefing D6, D8](../../project/briefing.md)
