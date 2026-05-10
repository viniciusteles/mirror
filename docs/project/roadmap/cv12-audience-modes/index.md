[< Roadmap](../index.md)

# CV12 — Audience Modes

**Status:** Future
**Goal:** Let Mirror adapt explanation depth and vocabulary to the user's
operating context without changing underlying truth.

---

## Scope

Initial modes:

```text
technical
non-technical
```

Audience mode affects how Mirror explains:

- Builder briefings
- coherence summaries
- skill outputs
- blockers and error messages
- onboarding
- generated plans and test guides
- persona explanation strategy

Audience mode does not affect:

- facts
- memory retrieval
- journey state
- task status
- coherence rules
- whether something is considered coherent

The principle is: audience mode changes translation, not truth.

---

## Relationship to CV10

CV10 should keep the UoC model compatible with future audience modes by
separating semantic ids from human-facing explanations. CV10 does not deliver
audience-mode behavior.
