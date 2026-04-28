[< CV7.E1 Observability](../index.md)

# CV7.E1.S3 — Routing eval + proportionality eval

**Status:** Planned  
**Epic:** CV7.E1 — Pipeline Observability & Evals  
**Requires:** CV7.E1.S2 (evals harness)  
**Goal:** Two additional evals plugged into the existing harness; together with `extraction`
they give E2 a complete behavioral baseline to regress against.

---

## Two evals, different purposes

### `routing` — persona detection behavioral contract

Tests `detect_persona()` on canned queries. Documents which messages should
route where, covering clear domain cases, ambiguous inputs, and null cases
(no persona expected).

**Why in `evals/` and not `tests/`?**  
Today `detect_persona()` is keyword-based and deterministic — it could live in
`tests/`. It goes in `evals/` because CV7.E2 will replace it with an LLM
classifier, at which point this exact fixture set becomes the regression net for
non-deterministic behavior. Moving it then would require restructuring; placing
it here now costs nothing.

**Probe shape:** `{query, expected_persona: str | None}`. A probe passes if
`detect_persona(query)` returns `expected_persona` as the top match (or returns
empty when `None` is expected).

**Threshold:** 0.85 — routing is deterministic today, so near-perfect is the bar.

**15 probes covering four categories:**

| Category | Count | Examples |
|----------|-------|---------|
| Clear domain match | 8 | code/bug → engineer; writing/article → writer; symptom/health → doctor |
| Ambiguous — highest-signal wins | 3 | "thinking about how to structure my code" → engineer over thinker |
| Null — no persona expected | 3 | existential open question with no domain keywords → None |
| Multi-keyword accumulation | 1 | multiple engineer keywords in one query → engineer with higher score |

### `proportionality` — extraction does not over-extract trivial input

Tests that short, casual, lived-in messages produce zero or near-zero memories.
This is the watch probe described in `draft-analysis.md §8.1`: if it fires
consistently, the expression pass earns its way back into scope as CV8 work.

**Why this matters:**  
The expression pass (deferred from CV7) solves proportionality at the response
level. This probe measures the same signal at the extraction level: does the
extraction pipeline treat casual exchanges as memorable? It should not.

**Probe shape:** canned short/casual transcript → `extract_memories()` → expects
`len(memories) == 0`.

**Threshold:** 0.8 — a single false positive is acceptable; systematic
over-extraction is not.

**5 probes:**

| Probe id | Transcript | Expected |
|----------|-----------|---------|
| `casual-greeting` | "Hey, how are you?" / "Fine thanks" / "Cool" | 0 memories |
| `logistical-question` | "What's the best way to get from Lisbon to Porto?" | 0 memories |
| `quick-factual` | "What year was Python first released?" / "1991" / "Thanks" | 0 memories |
| `status-check` | "How is the project going?" / "Good, steady progress" / "Great" | 0 memories |
| `small-talk` | Brief back-and-forth about weather/plans with no substance | 0 memories |

---

## Implementation

No changes to `runner.py` or `types.py`. Two new files follow the exact pattern
established in S2.

```
evals/routing.py          # 15 probes, THRESHOLD = 0.85
evals/proportionality.py  # 5 probes, THRESHOLD = 0.80
```

**`evals/routing.py`** imports and calls `detect_persona()` directly from
`memory.services.identity` via a `MemoryClient`. Since the function is
deterministic, each probe executes in milliseconds and costs nothing.

**`evals/proportionality.py`** calls `extract_memories()` directly, like the
extraction eval. Hits real LLM — costs cents per run.

---

## Files changed

| File | Change |
|------|--------|
| `evals/routing.py` | New: 15 routing probes, `THRESHOLD = 0.85` |
| `evals/proportionality.py` | New: 5 proportionality probes, `THRESHOLD = 0.80` |
| `tests/unit/memory/evals/test_eval_modules.py` | New: structural tests — both modules expose valid `PROBES` and `THRESHOLD` |

---

## Tests

The probe functions themselves are not unit-tested (they call real LLM or real
detection logic). The structural tests verify the module contract the runner
depends on.

**`test_eval_modules.py`:**
- `evals.routing` exposes `PROBES` as a non-empty list of `EvalProbe`
- `evals.routing` exposes `THRESHOLD` as a float between 0 and 1
- `evals.proportionality` exposes `PROBES` as a non-empty list of `EvalProbe`
- `evals.proportionality` exposes `THRESHOLD` as a float between 0 and 1
- All probes in both modules have non-empty `id` and `description`
- All probe `id` values are unique within each module

---

## Constraints

- `routing.py` must not hit any LLM — it calls only `detect_persona()`.
- `proportionality.py` uses real LLM calls; requires `OPENROUTER_API_KEY`.
- Both modules must be runnable independently:
  `uv run python -m memory eval routing`
  `uv run python -m memory eval proportionality`
- The routing eval requires a seeded database (personas with routing metadata).
  A missing/empty persona store causes probes to fail gracefully, not crash.

---

## Done condition

- `uv run python -m memory eval routing` runs and reports per-probe results
- `uv run python -m memory eval proportionality` runs and reports per-probe results
- All structural unit tests pass in CI
- S4 and S5 can proceed without changes to the harness

---

**See also:** [CV7.E1 index](../index.md) · [draft-analysis §4.5](../../draft-analysis.md) · [draft-analysis §8.1](../../draft-analysis.md)
