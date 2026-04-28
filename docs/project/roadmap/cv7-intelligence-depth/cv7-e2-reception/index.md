[< CV7 Intelligence Depth](../index.md)

# CV7.E2 — Reception & Conditional Composition

**Epic:** A small reception step classifies each turn; the system prompt loads only what reception activates
**Status:** Done
**Depends on:** CV7.E1 (observability + evals)
**Prerequisite for:** CV7.E3, CV7.E4

---

## What This Is

Today `mm-mirror` always loads the same identity bundle: `self/soul`,
`ego/identity`, `ego/behavior`, the active persona, the active journey,
attachments above a similarity threshold. Every token is paid every turn.
The principle from briefing — *every token in the prompt must earn its
place* — is not honored.

This epic introduces a small classifier LLM call (**reception**) that runs
before composition and decides what activates for this turn. The composer
becomes conditional: it loads identity only when reception flags an
identity-touching turn; it loads shadow only when reception flags evidence
of shadow material; it picks the right persona and journey from a richer
signal than the current keyword/embedding heuristic.

The architectural payoff is that the response pipeline becomes a **named
series of steps with typed contracts**, not one big prompt assembly. Once
that exists, future changes (compaction, topic-shift detection, shadow
surfacing, expression pass if it returns) plug in as additional steps.

---

## Done Condition

- a `reception()` function exists in `src/memory/intelligence/reception.py`
  that classifies a user message in one LLM call and returns
  `{personas: [...], journey, touches_identity, touches_shadow}` plus
  fallback semantics on failure
- `mm-mirror` invokes reception before composing context; the keyword/
  embedding detection is demoted to fallback
- `load_mirror_context` is conditional: `self/soul` and `ego/identity`
  load only when `touches_identity == true`; the `shadow` layer loads
  only when `touches_shadow == true` AND structural shadow content
  exists (the structural shadow layer ships in CV7.E4.S4)
- session-scoped sticky persona/journey continues to work; reception
  can override per-turn when the message clearly belongs elsewhere
- routing eval (`routing.py` from CV7.E1.S3) covers reception's outputs
  and threshold is met
- per-turn token count drops on conversational/operational turns vs the
  CV6 baseline; measured against the eval harness

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV7.E2.S1 | Reception MVP — classifier returns four axes; eval-driven | Done |
| CV7.E2.S2 | Conditional composition in `load_mirror_context` (identity + shadow gates) | Done |
| CV7.E2.S3 | Reception as the source of truth for persona/journey routing in `mm-mirror` | Done |

---

## Out of scope (see CV7 index §Resolved decisions)

- **`mode` axis and expression pass.** Reception ships with four axes,
  not five. The `mode` classification (conversational / compositional /
  essayistic) and the post-generation expression pass are deferred from
  CV7. See [draft-analysis.md §8.1](../draft-analysis.md) for the watch
  criterion that would bring them back.

---

## Sequencing

```text
S1 (reception MVP)
  └── S2 (conditional composition)
        └── S3 (reception as routing source of truth)
```

S1 lands the classifier behind a feature flag, with eval coverage from day
one. S2 wires its output into the composer, gated by `touches_identity` and
(once E4.S4 ships the schema) `touches_shadow`. S3 promotes reception from
"co-existing with detection" to "the canonical routing path", with detection
as fallback.

---

## See also

- [CV7 index](../index.md)
- [draft-analysis §4.2 — Reception as a single classifier-LLM call](../draft-analysis.md)
- [draft-analysis §6 — CV7.E2 description](../draft-analysis.md)
- Alisson's `server/reception.ts` — reference for prompt structure and decision rules
