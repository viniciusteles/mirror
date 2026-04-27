[< CV7 Intelligence Depth](../index.md)

# CV7.E1 — Pipeline Observability & Evals

**Epic:** Every LLM-backed step is logged and inspectable; behavior can be evaluated across versions, models, and prompt revisions
**Status:** Planned
**Prerequisite for:** CV7.E2, CV7.E3, CV7.E4

---

## What This Is

Today the mirror runs several LLM-backed steps — memory extraction, journal
classification, task extraction, week-plan parsing, journey detection — and
none of them are observable after the fact. There is no log of what was sent,
what came back, how long it took, what it cost. There is no way to compare
two versions of a prompt against the same input. There is no regression net
when an extraction prompt is edited.

CV7 is going to add several more LLM-backed steps (reception, two-pass
extraction, summary generation, possibly search reranking). Adding them
without observability would compound the blindness. This epic builds the
instrument first.

Two pieces:

- **Logging substrate.** Every LLM call writes a row to a structured table:
  role, model, prompt, response, tokens in/out, cost, latency, conversation,
  session, related artifact id (memory, identity, etc.). Behind a flag so
  storage cost is paid only when investigating.
- **Evals harness.** A separate `evals/` tree, distinct from `tests/`, with
  its own runner. Each eval is a probe set with a threshold — non-deterministic,
  cost money per run, run on demand. Behavior regressions become visible
  before they ship.

---

## Done Condition

- a `llm_calls` table exists with the canonical schema and is written by
  every existing LLM-backed step in `src/memory/intelligence/`
- the logging is gated by an env flag (`MEMORY_LOG_LLM_CALLS=1`) so it does
  not always pay storage cost
- a `python -m memory inspect llm-calls` CLI exists that filters by
  conversation, session, role, and time range
- an `evals/` tree exists with a runner, a probe-set type, and a threshold
  contract
- at least three evals are in place and runnable: `extraction`, `routing`
  (persona/journey detection on canned messages), and `proportionality`
  (the watch probe for the deferred expression pass — see draft-analysis §8.1)
- baseline scores for all three evals are recorded and stored in the worklog
  before E2 ships
- developer-guide documentation explains when to run evals and the contract
  for adding a new one

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV7.E1.S1 | `llm_calls` log table + instrumentation hooks at every existing call site | Planned |
| CV7.E1.S2 | Evals harness skeleton + first eval (`extraction`) | Planned |
| CV7.E1.S3 | Routing eval + proportionality eval | Planned |
| CV7.E1.S4 | `inspect llm-calls` CLI for trace inspection | Planned |
| CV7.E1.S5 | Baseline measurement run + worklog of baseline scores | Planned |

---

## Sequencing

```text
S1 (log table + instrumentation)
  ├── S2 (evals harness + extraction eval)
  │     └── S3 (routing + proportionality evals)
  ├── S4 (inspect CLI)
  └── S5 (baseline measurement)
```

S1 is the substrate. S2 builds the harness; once it exists, S3 adds two more
evals on the same shape. S4 is a small UX layer over S1 and can ship any
time after S1 lands. S5 closes the epic by recording the numbers everything
else in CV7 will be measured against.

---

## See also

- [CV7 index](../index.md)
- [draft-analysis §5.6 — Observability before optimization](../draft-analysis.md)
- [draft-analysis §7 — Success metrics](../draft-analysis.md)
- Alisson's [CV1.E8](https://github.com/) (Pipeline Observability & Eval) — the inspiration; we build a smaller version here
