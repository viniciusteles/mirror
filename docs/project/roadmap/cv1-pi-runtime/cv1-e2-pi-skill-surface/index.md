[< CV1 Pi Runtime](../index.md)

# CV1.E2 — Pi Skill Surface

**Epic:** I can invoke the mirror from Pi  
**Status:** ✅ Done  
**Requires:** CV1.E1 (Shared Command Core)

---

## What This Is

Once the shared skill modules exist (CV1.E1), this epic adds the Pi-facing
interface: a `.pi/` directory with settings, skill wrappers using Pi's hyphenated
command naming, and the Pi extension that dispatches to Python.

Claude commands use colons (`mm:mirror`). Pi commands use hyphens (`mm-mirror`).
Both call the same `src/memory/skills/` modules.

---

## Done Condition

- `.pi/settings.json` enables Pi skill commands
- `.pi/skills/mm-mirror/`, `mm-consult/`, `mm-journey/`, etc. exist as thin wrappers
- Pi commands (`/mm-mirror`, `/mm-journey`) call `memory.skills.*` modules
- Claude commands (`/mm:mirror`, `/mm:journey`) are unchanged
- `.pi/extensions/mirror-logger.ts` exists and dispatches to `python -m memory conversation-logger`

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV1.E2.S1 | Add `.pi/` skeleton with settings and skill wrappers | ✅ |
| CV1.E2.S2 | Port mirror-logger extension against English runtime | ✅ |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV1.E1 Shared Command Core](../cv1-e1-shared-command-core/index.md) · [Pi Adoption Spike](../../../../process/spikes/pi-runtime-adoption-2026-04-17.md)
