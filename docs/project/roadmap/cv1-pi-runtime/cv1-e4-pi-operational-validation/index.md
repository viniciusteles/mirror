[< CV1 Pi Runtime](../index.md)

# CV1.E4 — Pi Operational Validation

**Epic:** The mirror runs on Pi  
**Status:** ✅ Done  
**Requires:** CV1.E2 (Pi Skill Surface) + CV1.E3 (Pi Session Lifecycle)

---

## What This Is

An end-to-end smoke validation of the full Pi interface against a real Pi
runtime. This is the CV1 done condition: a Pi session invokes `/mm-mirror`,
the response is logged, and memories are extracted at session end.

The validation approach mirrors the English migration smoke test: isolated
`HOME`/`MEMORY_DIR` to prevent production DB mutation, explicit verification
of each lifecycle event, and no assertion-free steps.

---

## Done Condition

- Pi is running with `.pi/settings.json` and the mirror extension loaded
- `/mm-mirror` activates Mirror Mode with identity loaded from the database
- Session messages are logged by the mirror-logger extension
- Session end triggers extraction (with journey set and ≥4 messages)
- Memories appear in `python -m memory list` scoped to the test journey
- Claude interface is unchanged: existing tests still pass
- No production database was touched during validation

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV1.E4.S1 | Pi smoke validation with isolated environment | ✅ |

---

**See also:** [CV1 Pi Runtime](../index.md) · [CV1.E2](../cv1-e2-pi-skill-surface/index.md) · [CV1.E3](../cv1-e3-pi-session-lifecycle/index.md) · [Pi Adoption Spike](../../../../process/spikes/pi-runtime-adoption-2026-04-17.md)
