[< Roadmap](../index.md)

# CV11 — Localization

**Status:** Future
**Goal:** Make Mirror support multiple human languages as a platform-level
surface, starting with `en-US` and `pt-BR`.

---

## Scope

Localization is broader than coherence. It affects:

- skill outputs
- Builder briefings
- journey and task summaries
- coherence summaries
- installer and onboarding text
- generated docs owned by Mirror

Localization changes language, not semantics. The same journey state, memory,
UoCs, tasks, and project facts should remain true across locales.

---

## Relationship to CV10

CV10 must keep UoC semantic ids separate from human-facing text so localization
can translate the surface later. CV10 does not deliver full localization.
