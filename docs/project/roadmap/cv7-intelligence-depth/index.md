[< Roadmap](../index.md)

# CV7 — Intelligence Depth

**Status:** In Progress
**Goal:** Improve the quality and depth of what the mirror remembers, how it routes a turn, what it puts in front of the model, and what it cultivates over time — without abandoning the principle that every token in the prompt must earn its place.

---

## What This Is

The first six CVs built a multi-runtime, multi-user, framework-grade
foundation. Identity is database-backed, runtime sessions are safe, the
extension model is real, onboarding is repeatable. The skeleton is solid.

CV7 turns the focus inward: **the intelligence layer itself**. Today the
mirror loads a fixed identity bundle for every turn, extracts memories with
a single LLM pass, retrieves them with in-process cosine + recency, and has
no instrument to see what its LLM-backed steps actually do. CV7 invests in:

- **observability** — instrument every LLM call so we can tune what we
  measure, and add an evals harness so we can guard behavior across changes
- **response intelligence** — a small reception classifier, conditional
  composition (only load identity layers when the turn invites them), shadow
  awareness as its own routing axis
- **extraction quality** — sharper prompt, two-pass extraction with
  deduplication, generated descriptors for routing
- **memory depth** — hybrid search 2.0 (lexical + semantic + dedupe),
  honest reinforcement (use vs retrieval, decay), consolidation as a
  first-class integration operation, **shadow as a structural layer** with
  readiness states and asymmetric activation

The full territorial analysis, comparing our state to Alisson's parallel
reconstruction (`mirror-mind`) and the broader field, lives in
[draft-analysis.md](draft-analysis.md). The four epics below are the result.

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|----------------------|--------|
| [CV7.E1](cv7-e1-observability/index.md) | Pipeline Observability & Evals | Every LLM call is logged and inspectable; behavior can be evaluated across versions, models, and prompt revisions | Done |
| [CV7.E2](cv7-e2-reception/index.md) | Reception & Conditional Composition | A small reception step classifies each turn (persona, journey, identity-touch, shadow-touch); the system prompt loads only what reception activates | Done |
| [CV7.E3](cv7-e3-extraction-quality/index.md) | Extraction Quality | Memory extracted from conversations is fewer, sharper, deduplicated against existing memory; descriptors for routing are generated and curated | In Progress |
| [CV7.E4](cv7-e4-memory-depth/index.md) | Memory Depth: Search, Reinforcement, Shadow | Hybrid retrieval scales beyond in-process scan; reinforcement reflects use, not just retrieval; consolidation promotes raw memories into structural identity content; shadow is a structural layer with readiness states | Planned |

---

## Done Condition

CV7 is done when:

- every LLM-backed step (extraction, journal classification, task extraction,
  week-plan parsing, reception, search reranking) writes to a structured log
  table that can be inspected per-conversation and per-role
- a versioned evals harness exists separately from `tests/` and covers at
  minimum extraction quality, journey/persona routing, reception axes
  (including `touches_identity` and `touches_shadow`), and retrieval
  relevance
- reception runs on every Mirror Mode turn and its output drives composition;
  identity layers (`self/soul`, `ego/identity`) compose conditionally on
  `touches_identity`; the shadow layer composes conditionally on
  `touches_shadow` plus structural-content gating
- extraction is two-pass (candidate + curate-against-existing) and produces
  fewer, higher-signal memories per conversation than the current single-pass
  baseline, measured by the eval harness
- a `shadow` layer exists in the `identity` table as a peer of `self` and
  `ego`; raw shadow material is collected via the memory destination side and
  promoted to the structural layer via the consolidation operation; readiness
  states are tracked
- hybrid search uses lexical + semantic fusion with dedup, scales beyond the
  current in-process scan, and improves measured retrieval relevance against
  the eval harness baseline
- `mm-consolidate` and `mm-shadow` skills exist and have been used at least
  once each end-to-end on real material
- per-turn cost and latency stay inside their envelopes (set during the E1
  planning pass)

---

## Sequencing

```text
E1 (observability + evals)
  └── E2 (reception + conditional composition)
        └── E3 (extraction quality)
              └── E4 (search, reinforcement, consolidation, shadow)
```

E1 first because every other CV7 story changes LLM behavior — without
observability and a regression net, we tune blind. E2 before E3 because
once reception lands, downstream signals (per-turn classification) are
available to extraction and search. E4 last because it depends on the
sharper extraction signals from E3 to have meaningful material to work
with. E1.S2 (the evals harness itself) can begin in parallel with the
later stories of E1.S1; the rest of the chain is sequential.

---

## Resolved decisions (planning phase)

These decisions were made during CV7 analysis and constrain the planning
of subsequent epics:

- **Shadow is both a structural layer and a memory destination**
  (resolved 2026-04-26 via Mirror Mode session with the therapist persona).
  Architectural consequence: a `shadow` layer in the `identity` table,
  peer to `self` and `ego`; readiness states (`observed → candidate →
  surfaced → acknowledged → integrated`) on memories; a dedicated
  `touches_shadow` axis in reception; consolidation as the integration
  operation. See `draft-analysis.md` §5.5 and decisions.md.
- **Expression pass and `mode` deferred from CV7** (resolved 2026-04-26).
  Reception ships with four axes (`personas, journey, touches_identity,
  touches_shadow`), not five. The proportionality problem the expression
  pass solves has not been measured for us yet; we ship CV7 without it
  and add a proportionality probe to the eval harness in E1. If the probe
  surfaces real corrosion, the expression pass returns as a focused
  mini-CV in CV8 with its own success criteria. See draft-analysis.md
  §8.1 and decisions.md.

---

## Open questions parked for the planning pass

- **Reception model choice.** Same model as extraction (Gemini 2.5 Flash
  Lite) or a smaller/faster pick? Resolved by an eval comparison spike
  inside E2.S1 planning.
- **Generated descriptors storage.** A `summary` column on the `identity`
  table, or a sidecar table that can hold descriptors for any kind of
  content? Resolved inside E3.S4 planning.
- **Per-turn cost envelope ceiling.** §7 of the analysis commits to
  cost-as-envelope but leaves the number open. Resolved during E1
  planning, against current per-turn cost data.
- **Promotion mechanism for shadow consolidation** — auto by repetition,
  manual by user acknowledgment, or hybrid? Highest-leverage decision in
  E4. Resolved during E4.S3 / E4.S4 planning, likely via Mirror Mode.

---

## See also

- [draft-analysis.md](draft-analysis.md) — territorial analysis, success
  metrics, decisions log
- [Briefing](../../briefing.md)
- [Decisions](../../decisions.md)
- [CV6](../cv6-intelligence-runtime-maturity/index.md) — the foundation CV7 builds on
