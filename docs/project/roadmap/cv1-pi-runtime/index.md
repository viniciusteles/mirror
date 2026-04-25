[< Roadmap](../index.md)

# CV1 — Pi Runtime ✅

**Status:** Done  
**Goal:** Make `mirror` dual-interface — Claude Code plus Pi — without rewriting the core.

---

## What This Is

Pi (`badlogic/pi-mono/tree/main/packages/coding-agent`) is a local AI coding agent runtime built on TypeScript.
It is model-agnostic and does not require Claude Code. CV1 makes the mirror run
on Pi by adding a Pi interface layer while keeping the Python `memory` core
unchanged.

The strategy: one implementation, two frontends. Claude Code and Pi both call
the same Python core. Neither interface owns behavior.

---

## Epics

| Code | Epic | User-visible outcome |
|------|------|---------------------|
| CV1.E1 | Shared Command Core | The mirror speaks from one place |
| CV1.E2 | Pi Skill Surface | I can invoke the mirror from Pi |
| CV1.E3 | Pi Session Lifecycle | Pi sessions are remembered |
| CV1.E4 | Pi Operational Validation | The mirror runs on Pi |

---

## Done Condition

CV1 is done when:
- All four epics are complete
- A Pi session can invoke `/mm-mirror`, have the response logged, and have memories extracted at session end
- The Claude Code interface is unchanged and all existing tests still pass

---

## Sequencing

E1 → E2 and E1 → E3 are sequential. E2 and E3 can overlap once E1 is done.
E4 validates the full stack and requires E2 and E3 to be complete.

```
E1 (Shared Command Core)
  ├── E2 (Pi Skill Surface)
  └── E3 (Pi Session Lifecycle)
        └── E4 (Pi Operational Validation)
```

---

**See also:** [CV0 English Foundation](../cv0-english-foundation/index.md) · [Briefing D6](../../../project/briefing.md) · [Briefing D8](../../../project/briefing.md)
