[< Roadmap](../index.md)

# CV3 — Pi Skill Parity

**Status:** ✅  
**Goal:** Every skill available in Claude Code is also available in Pi.

---

## What This Is

CV1 gave Pi one skill: `/mm-mirror`. Claude Code has 18. CV3 closes that gap.

The strategy follows CV2's discipline: Pi wrappers are thin dispatchers that
call `python -m memory <command>`. Before wrappers can be written, the Python
CLI must expose every operation a skill needs. That is E1. E2 writes the
wrappers. E3 handles the two intelligence skills that require multi-LLM calls.

**Exclusion: `mm:build`**  
Builder Mode is Claude Code-specific. It relies on Claude Code's editing and
file tools (Read, Edit, Write, Bash) to work with code. Pi is itself a code
agent runtime — Builder Mode on Pi is redundant. `mm:build` is not ported.

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|---------------------|--------|
| [CV3.E1](cv3-e1-cli-completeness/index.md) | CLI Completeness | Every skill operation is reachable via `python -m memory` | ✅ |
| [CV3.E2](cv3-e2-pi-skill-wrappers/index.md) | Pi Skill Wrappers | 15 skills available on Pi | ✅ |
| [CV3.E3](cv3-e3-pi-intelligence-skills/index.md) | Pi Intelligence Skills | `mm:consult` and the later reference-extension example `mm:review-copy` available on Pi | ✅ |
| [CV3.E4](cv3-e4-skill-architecture-cleanup/index.md) | Skill Architecture Cleanup | All skills call `python -m memory` directly — no run.py | ✅ |

---

## Skills Inventory

| Skill | Has run.py | CLI exists | Pi status | Notes |
|-------|-----------|------------|-----------|-------|
| mm:mirror | — | ✅ | ✅ done (CV1) | banners in `memory.skills.mirror.main()` |
| mm:backup | — | ✅ | ✅ done (CV3.E2) | SKILL.md only |
| mm:mute | — | ✅ | ✅ done (CV3.E2) | via `conversation-logger mute/unmute` |
| mm:new | — | ✅ | ✅ done (CV3.E2) | via `conversation-logger switch` |
| mm:seed | — | ✅ | ✅ done (CV3.E2) | SKILL.md only |
| mm:help | — | — | ✅ done (CV3.E2) | documentation only |
| mm:journeys | — | ✅ | ✅ done (CV3.E2) | `python -m memory journeys` via `cli/journeys.py` |
| mm:journal | — | ✅ | ✅ done (CV3.E2) | `python -m memory journal` |
| mm:journey | — | ✅ | ✅ done (CV3.E2) | `python -m memory journey` |
| mm:memories | — | ✅ | ✅ done (CV3.E2) | `python -m memory memories` |
| mm:conversations | — | ✅ | ✅ done (CV3.E2) | `python -m memory conversations` |
| mm:recall | — | ✅ | ✅ done (CV3.E2) | `python -m memory recall` |
| mm:tasks | — | ✅ | ✅ done (CV3.E2) | `python -m memory tasks` via `tasks_cmd.py` |
| mm:week | — | ✅ | ✅ done (CV3.E2) | `python -m memory week` |
| mm:save | — | ✅ | ✅ done (CV3.E2) | Pi limitation: no JSONL transcript |
| mm:consult | — | ✅ | ✅ done (CV3.E3) | `python -m memory consult`; logic in `cli/consult.py` |
| mm:review-copy | — | — | ✅ done (CV3.E3) | model-driven; SKILL.md only; later reclassified in CV6 as a reference extension example |
| mm:build | — | ✅ | excluded | hybrid: `python -m memory build load` + Claude reads docs natively |

---

## Done Condition

CV3 is done when:
- All 15 portable skills are invocable from Pi
- Each Pi skill wrapper calls `python -m memory <command>`
- Claude Code interface is unchanged and all existing tests still pass

---

## Sequencing

E1 → E2 (wrappers require CLI). E3 can run in parallel with E2 once E1 is done.

```
E1 (CLI Completeness)
  ├── E2 (Pi Skill Wrappers)
  └── E3 (Pi Intelligence Skills)
```

---

**See also:** [CV2 Runtime Portability](../cv2-runtime-portability/index.md) · [CV4 Intelligence Depth](../index.md) · [Runtime Interface](../../runtime-interface.md)
