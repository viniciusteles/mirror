[< CV7 Intelligence Depth](../index.md)

# CV7.E4 — Memory Depth: Search, Reinforcement, Shadow

**Epic:** Hybrid retrieval scales beyond in-process scan; reinforcement reflects use, not just retrieval; consolidation promotes raw memories into structural identity content; shadow becomes a structural layer with readiness states
**Status:** Planned
**Depends on:** CV7.E1 (eval harness), CV7.E2 (reception axes including `touches_shadow`), CV7.E3 (sharper extraction signal)

---

## What This Is

The first three epics fix what the mirror *takes in* and *routes through*.
This epic fixes what it *carries* and *cultivates over time*.

Four areas, each with its own architectural shift:

- **Hybrid search 2.0.** Today retrieval loads every memory into Python
  and ranks in-process with cosine + recency + reinforcement + relevance.
  This will not scale. Replace with FTS5 + indexed vectors (sqlite-vec or
  similar) + RRF fusion + MMR/dedupe. The data model survives; the access
  pattern changes.
- **Honest reinforcement.** Today reinforcement = `log1p(access_count)/3`
  with no decay. Memories accessed in 2024 stay "reinforced" forever.
  Distinguish *retrieval* (memory was injected) from *use* (memory was
  actually referenced in the response), decay both, and tune weights with
  the eval harness instead of by feel.
- **Consolidation as integration.** Reframed from a memory hygiene step
  into the central operation that promotes raw extracted memories into
  structural identity content. A `mm-consolidate` skill surfaces clusters
  of similar memories and proposes a merge, a structural shadow promotion,
  or a direct identity-layer update. The user reviews. Provenance is
  preserved. The promotion mechanism is the highest-leverage open question
  in CV7.
- **Shadow as a structural layer.** Per the resolution recorded in
  draft-analysis.md §5.5: shadow is *both* a memory destination and a
  structural layer, with consolidation as the bridge. This story builds
  the structural side: a `shadow` layer in the `identity` table (peer to
  `self` and `ego`), readiness states on memories, the `mm-shadow`
  periodic surfacing pass, and asymmetric composition rules (provenance
  required, evidence threshold, conservative activation).

---

## Done Condition

- hybrid search uses FTS5 + indexed vectors + fusion + dedupe; works
  efficiently against memory pools well beyond the current scan limit;
  retrieval-relevance eval (CV7.E1) shows improvement vs baseline
- the memories table has new columns: `last_accessed_at`, `use_count`
  (separate from `access_count`), and `readiness_state` enum
  (`observed | candidate | surfaced | acknowledged | integrated`)
- reinforcement scoring uses use, retrieval, and decay; weights are
  tuned via eval harness, not heuristic guesses
- a `mm-consolidate` skill exists; it has been used end-to-end on real
  material at least once; merges and identity-layer updates are recorded
  with provenance
- a `shadow` layer exists in the `identity` table; it is composed into
  the prompt only when `touches_shadow` (E2.S1) is true AND the layer
  has `acknowledged+` content; composition format includes provenance
- a `mm-shadow` skill exists; it scans recent memories + structural
  shadow content and surfaces candidate observations with provenance for
  user review; accepted observations transition source memories from
  `observed`/`candidate` to `acknowledged` and write to the structural
  shadow layer
- the promotion mechanism (auto-by-repetition, manual-by-acknowledgment,
  or hybrid) is decided and documented in decisions.md before E4.S3 ships

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV7.E4.S1 | Hybrid search 2.0 (FTS5 + sqlite-vec + RRF + MMR) | Done |
| CV7.E4.S2 | Reinforcement honest (use vs retrieval, decay, eval-tuned weights, schema migration) | Done |
| CV7.E4.S3 | Consolidation as integration (`mm-consolidate` skill, promotion mechanism) | Done |
| CV7.E4.S4 | Shadow as structural cultivation (`shadow` layer + readiness states + `mm-shadow` skill + asymmetric composition) | Planned |
| CV7.E4.S5 | *(Stretch)* Cross-conversation summaries / "weekly pass" | Deferred |

---

## Sequencing

```text
S1 (hybrid search 2.0) — independent, ship anytime
S2 (reinforcement honest + readiness_state column)
  └── S3 (consolidation, depends on readiness states)
        └── S4 (shadow structural layer, depends on consolidation)
S5 (weekly pass) — deferred; revisit after S1–S4 prove themselves in use
```

S1 is mostly independent — search infrastructure can change without
touching reinforcement, consolidation, or shadow. S2 introduces the
schema columns that S3 and S4 both need (`readiness_state` lives on
memories generally, not just shadow), so the migration is planned once.
S3 builds the consolidation operation; S4 uses it for shadow promotion.
S5 is deliberately deferred — it's the agent equivalent of sleep/dream
consolidation and deserves its own design pass once we've used S3/S4 on
real material.

---

## Open questions parked for the planning pass

- **Promotion mechanism for shadow consolidation** — auto by repetition,
  manual by user acknowledgment, or hybrid? The single highest-leverage
  decision in CV7. Resolved during E4.S3 / E4.S4 planning, likely via
  Mirror Mode discussion with the therapist persona.
- **Vector index choice** — sqlite-vec vs sqlite-vss vs another route?
  Resolved during E4.S1 planning.

---

## See also

- [CV7 index](../index.md)
- [draft-analysis §5.5 — Shadow needs structural treatment](../draft-analysis.md)
- [draft-analysis §6 — CV7.E4 description](../draft-analysis.md)
- The Mirror Mode therapist session of 2026-04-26 (recorded in conversation history) — the canonical derivation of the shadow architecture
