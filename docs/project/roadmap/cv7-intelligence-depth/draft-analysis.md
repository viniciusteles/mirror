[< CV7](index.md)

# CV7 — Draft Analysis

**Date:** 2026-04-26
**Status:** Draft — input for CV7 planning, not a roadmap commitment yet
**Author:** engineer (Builder Mode)

---

## 1. Purpose of this document

CV7 is named "Intelligence Depth" but its definition in the roadmap is a list of
candidate areas, not a plan: better extraction prompts, richer Jungian layering
(shadow), reinforcement tuning, smarter hybrid search, signal-quality.

Before we plan it, we need a **map of the territory**:

- what our current intelligence stack actually does today,
- what Alisson's parallel reconstruction (`~/dev/workspace/mirror-mind`) has
  done in the same territory,
- what the broader field of agent memory and pipelined response systems
  teaches,
- and where, between these, our highest-leverage moves are.

This document is that map. It ends with a proposed shape for CV7 — themes,
candidate epics and stories, dependencies, and open questions. It is
deliberately a draft, written to be argued with.

---

## 2. The territory in one sentence

Intelligence Depth has two faces, and they tend to get conflated.

- **Response intelligence** — what happens *during* a turn. How the system
  composes the prompt, decides which content to load, generates, and shapes the
  output before the user sees it.
- **Memory intelligence** — what happens *between* turns. How the system
  extracts, stores, retrieves, and reuses what was said before.

Today our CV7 description is mostly memory-flavored (extraction, search,
layering, reinforcement). Alisson's parallel work is overwhelmingly
response-flavored (reception, conditional composition, expression pass,
multi-persona). **CV7 should consciously pick which face it is — or, more
likely, scope itself across both, in an order that respects their dependencies.**

---

## 3. Where we are today

### 3.1 Memory pipeline (current)

`src/memory/intelligence/` is a thin, working stack:

| Stage | File | What it does |
|---|---|---|
| Extraction | `extraction.py` | One LLM call (Gemini Flash Lite) at end of conversation. Produces 0–5 typed memories with `{title, content, context, memory_type, layer, tags, journey, persona}`. Same module also runs journal classification, task extraction, week-plan extraction. |
| Embedding | `embeddings.py` | OpenAI `text-embedding-3-small` via OpenRouter, 1536d, stored as bytes in SQLite. |
| Search | `search.py` | Hybrid: cosine + recency (90-day half-life) + reinforcement (`log1p(access_count)/3`) + a static `relevance_score` column. Default weights `0.6/0.2/0.1/0.1`. Loads **all** memories into memory and ranks in Python. Logs access for the top N. |
| Routing | `client.detect_persona/detect_journey` | Lightweight, in-context detection used by `mm-mirror` to pick the active persona/journey when not explicit. |

### 3.2 Memory model

- **Layers:** `self`, `ego`, `shadow` declared as Jungian; in practice almost
  everything lands in `ego`. `shadow` exists in the schema and the
  extraction prompt but is not actively cultivated.
- **Memory types:** decision, insight, idea, journal, tension, learning,
  pattern, commitment, reflection — flat enum, no hierarchy.
- **Persona / journey** stamped per memory; attachments stored per journey
  with their own embeddings and similarity threshold (0.4 in Mirror Mode).
- **Reinforcement:** `memory_access_log` rows + `access_count` aggregate.
  Used in scoring; not yet used to consolidate or promote across layers.

### 3.3 Response pipeline (current)

This is where the gap with Alisson is largest. We do **not** have a runtime
pipeline. The mirror runtime today is, structurally:

1. `mm-mirror` skill assembles a single big context block (identity + memories
   + journey-path + attachments) via `MemoryClient.load_mirror_context`.
2. The host runtime (Pi or Claude Code) calls the LLM once with that block
   plus the user message.
3. After the response, conversation logger appends; at conversation end,
   `extract_memories` + `extract_tasks` run.

Implications:

- **No reception layer.** Persona/journey detection is done in `client.py` by
  keyword/embedding heuristics, not by an LLM classifier. It's good enough for
  routing, but it cannot reason about *touches identity*, *form vs. topic*,
  *out-of-pool*, or *topic shift*.
- **No conditional composition.** `load_mirror_context` always loads the same
  bundle (modulo persona/journey). Every token is paid every turn.
- **No expression pass.** Form rules sit inside the persona/ego prompt and
  must compete with substance for the model's attention.
- **No observability of the pipeline.** We have no per-call logging table, no
  evals harness, no comparison runner. We tune extraction by reading
  conversations and editing the prompt — a closed loop with one observation
  point.

This is not a criticism of the current design — it's the natural shape of a
single-runtime mirror that ran inside Claude Code. CV7 is the moment to
question it.

---

## 4. What Alisson did

`~/dev/workspace/mirror-mind` is the same idea, reconstructed in TypeScript on
top of `pi-ai`/`pi-agent-core` as a server with thin adapters. He skipped
long-term memory entirely in early CVs and instead invested deeply in
**response intelligence**. The relevant work for CV7 is concentrated in:

- `docs/product/memory-taxonomy.md` and `memory-map.md` — the conceptual model
- `docs/product/prompt-composition/index.md` — the canonical pipeline doc
- `server/reception.ts` (533 lines) — the classifier
- `server/identity.ts` — `composeSystemPrompt` with conditional layers
- `server/expression.ts` — post-generation form pass
- `server/summary.ts` — descriptor generation for routing
- `evals/routing.ts` + `evals/scope-routing.ts` — eval harness
- CV1.E7 (Response Intelligence, 9 stories, mostly shipped)
- CV1.E8 (Pipeline Observability & Eval, drafts)

What follows is what I think actually deserves to inform CV7. I'm not
recommending we copy his stack; I'm extracting the *patterns* that survive
the architectural difference.

### 4.1 Memory taxonomy on two orthogonal axes

His clearest contribution is conceptual, not code. Memory is not a single
shape — it is a coordinate on **two axes**:

- **Cognitive role** (what the memory is for): Attention, Identity, Episodic,
  Procedural, Semantic, Prospective, Reflexive.
- **Storage mechanism** (how it's read/written): Identity layers, Episodic
  entries, Records, Attachments, Semantic index, KV.

The grid forces clarity: when a new "memory" feature is proposed, you ask
*which role* and *which mechanism* — and most confusion (e.g., is shadow a
layer? a record? a memory type?) dissolves on contact with the grid. The
**Structure vs Memory** distinction inside this taxonomy is also load-bearing
for us: shadow as a structural layer (psychic architecture) is a different
move than shadow as an extracted memory type.

We currently lack this vocabulary. Our `layer` enum mixes the structural
(self/ego — psyche) with the operational (`shadow` as a destination for
extracted tensions). This conflation will hurt as CV7 expands the system.

### 4.2 Reception as a single classifier-LLM call

Alisson's `receive()` is a small, fast LLM call that returns:

```ts
{
  personas: string[],            // 0..N, ordered, leading first
  organization: string | null,
  journey: string | null,
  mode: "conversational" | "compositional" | "essayistic",
  touches_identity: boolean,
  would_have_persona: string | null,
  would_have_organization: string | null,
  would_have_journey: string | null,
}
```

The decisions encoded in its system prompt are themselves the IP:

- **Form beats topic.** A short first-person statement on a deep topic stays
  conversational. The user's *register* dominates the *subject*.
- **Lighter-mode tiebreaker.** Default `conversational`. The cost of
  under-shaping is small (user can ask for more); the cost of over-shaping is
  silent corrosion (every casual turn becomes an essay).
- **Identity-conservative tiebreaker.** Default `touches_identity: false`.
  Same logic: loading soul + identity on operational turns is silent token
  waste plus tonal mismatch.
- **Sole-scope-in-domain rule.** If exactly one scope's descriptor covers the
  message's domain, that scope activates. Returning null is a routing bug.
- **Action verbs dominate topic.** "Write a post about X" → writer persona,
  not the X-domain persona.
- **Out-of-pool "would-have-picked".** When the session pool filters out a
  better candidate, surface it as a suggestion rather than ignore it.

The reception output then drives **conditional composition**: `self/soul` and
`ego/identity` only render if `touches_identity == true`; the persona block
only renders if a persona was picked; the scope blocks only render if
reception activated them. The session "pool" of allowed scopes constrains the
*candidate list reception sees*, not the composer's output. This is a clean
contract.

### 4.3 Expression pass — form as a separate step

`ego/expression` was extracted from the main prompt and turned into a
**post-generation rewrite call**:

1. Main generation produces a draft (never shown).
2. A small model rewrites the draft to fit `mode + ego/expression` — preserve
   substance, change form only.
3. The rewritten text is what streams to the user.

The point is not the cost — it's that **form rules stop competing with
substance for attention budget** during generation. The main model focuses
on what to say; the small model focuses on how to say it.

### 4.4 Generated summaries as routing descriptors

Reception doesn't read full layer/scope content — it reads short generated
summaries. There is a separate cheap-model role (`title`/`summary`) that, on
save, regenerates a 1–2 sentence descriptor optimized for routing. The
descriptor is what the router sees in its candidate list. This decouples
*content quality* from *routing quality* — long, layered ego content can be
edited freely without breaking routing, because routing reads the summary.

The summary prompt itself encodes constraints (no meta-framing, no "this
persona...", concrete domain language) so that the descriptor is reliably
informative.

### 4.5 Eval harness as a separate concept from tests

`evals/` is deliberately not in `tests/`. Different cost profile (cents per
run), different determinism, different failure semantics ("behavior drifted"
vs "code broke"). Each eval is a probe set with a threshold; it exits
non-zero below threshold. Run on demand, before shipping anything that could
shift LLM behavior.

The first eval is `routing.ts`: 22 fixtures of `{message, expected_persona}`
covering clear domain cases, ambiguous cases, meta/null cases, and rules
(production-verb-dominates-topic).

Without an eval harness, every change to extraction or routing prompts is
flying blind. This is, I think, the most directly portable piece for us.

### 4.6 Pipeline observability (planned, CV1.E8)

His draft for the next epic: a `llm_calls` log table that records every
invocation's prompt, response, model, tokens, latency, cost, session, and
entry id, behind an admin toggle. Plus per-turn re-runs against alternative
models for side-by-side comparison.

Two ideas there worth keeping:

- the **toggle** so you don't pay storage cost when not investigating
- the recorded **prompt is the source of truth** for finding token bloat,
  prompt drift across versions, and silent regressions

### 4.7 Things he did *not* do that we should not assume

- He has **no long-term memory yet** in `mirror-mind`. The Python POC has it
  (and we forked from there). His memory taxonomy is a roadmap, not an
  implementation.
- He has **no shadow layer**. His Jungian model is self / ego / personas;
  shadow is named in our docs but not in his.
- He has **no extraction prompt** at all in `mirror-mind` — that capability
  lives only in the POC.

So his code can teach us about the *response side* of intelligence and the
*conceptual frame* for memory. The actual extraction/search work in CV7 is a
Mirror-Mind-original problem; we are ahead of him there.

---

## 5. What the field teaches

Patterns from the broader space — production agent memory systems, retrieval
work, prompt engineering — that have crystallized enough to be worth applying.

### 5.1 Extraction as a multi-pass, not a single shot

Single-pass JSON-extraction (what we do today) hits three failure modes:

- low recall on long conversations (model misses memories late in transcript)
- low precision (LLM extracts trivia because the prompt asks for "0–5 memories")
- collapsing layer/type decisions inside the same call as content extraction

The state of the art is a two-stage pass:

1. **Candidate pass:** the LLM segments the conversation and proposes
   candidates with rough metadata.
2. **Curate pass:** a second call (sometimes the same model, sometimes
   smaller) deduplicates against existing memories, decides layer/type, and
   merges or discards.

Step 2 lets you give the curator the *existing memory pool* (as compact
descriptors, not full text) so duplicates are detected and similar memories
are merged rather than appended. This is the cheapest way to fight memory
bloat over time.

### 5.2 Semantic retrieval is rarely just cosine + recency

Production hybrid search systems converge on:

- **Query expansion** — the user question is rephrased into 1–3 search
  queries by a cheap LLM call; each query is searched independently and the
  results are merged (RRF or max-score). Critical when the user is vague or
  when the query language doesn't match the stored language.
- **Lexical signal** — BM25 or even simple keyword overlap, fused with
  semantic. SQLite has FTS5 built-in; this is one CREATE VIRTUAL TABLE away.
- **MMR or de-duplication on retrieval** — top-k cosine often returns five
  near-duplicates; Maximum Marginal Relevance (or a simple cosine-distance
  filter between results) yields more useful sets.
- **Cross-encoder rerank** — for the highest-stakes retrievals, a small
  reranker model scores the (query, candidate) pair directly. Adds
  latency; usually worth it only for top-20-into-top-5.

Our current scorer fuses semantic + recency + reinforcement + relevance, but
all signals are computed against a **single query embedding** loaded into
**all memories in process**. That works at our scale today (hundreds of
memories) and will not work at 10k+. The migration path is clear: SQLite
+ sqlite-vec or sqlite-vss for vector indexing, FTS5 for lexical, and a
fusion step.

### 5.3 Reinforcement deserves to be more than an access counter

Today reinforcement = `log1p(access_count)/3`. Two limitations:

- access count is incremented whenever a memory shows up in a top-N — even if
  the response didn't actually use it (no signal of *usefulness*, only of
  *retrieval*).
- there is no decay. A memory accessed heavily in 2024 stays "reinforced"
  forever.

A more honest reinforcement signal looks like:

- track *accesses* (already done) but also *uses* (was the memory cited in
  the response or fed to a downstream call?),
- decay both with the same half-life family as recency,
- separate **decay-on-time** from **decay-on-non-use**.

A simpler intermediate move: track a per-memory **last_accessed_at** and use
it to age out memories whose access count is purely historical. This is one
column and one scoring tweak.

### 5.4 Consolidation is a first-class operation, not a side effect

Alisson's taxonomy names this directly: "Episodic memory does not stay
episodic forever. Recurring facts get promoted into Identity. Repeated
patterns become Procedural rules. Significant events extract into Semantic."

In our system, extraction does the episodic → semantic consolidation, but
**nothing does memory → identity consolidation**. A pattern observed in 8
conversations stays an isolated `pattern` memory; it never updates the
`ego/behavior` layer that the user actually composes against. This is the
single biggest gap between "the mirror remembers" and "the mirror grows."

A consolidation step (manual at first, automatic later) would:

1. Group similar memories by semantic clustering.
2. Surface the cluster to the user with a proposed identity update.
3. On acceptance, edit the layer in the database and mark the source
   memories as "consolidated into identity" (preserved, but down-weighted in
   ranking).

This is the move that earns the "self-improving" claim in the journey
description.

### 5.5 Shadow needs structural treatment, not just a layer enum

> **Resolution recorded 2026-04-26** — this section captures the position
> arrived at in a Mirror Mode session with the therapist persona on the
> shadow architecture question (Q4). It is the canonical framing the rest
> of CV7 is planned against.

Shadow as a memory type is a starting point, but Jungian shadow work is
fundamentally about **patterns the user does not see in themselves**. The
mirror is uniquely positioned to surface those because it has the
across-conversation view the user lacks. The architectural decision
below follows from one Jungian observation: shadow is *not a category of
content*, it is *a region of the psyche defined by its relationship to
ego consciousness*. The same observation is ego content for someone who
has integrated it and shadow content for someone who hasn't. Architecture
follows function.

**Shadow is both a structural layer and a memory destination.** Neither
alone is enough.

- **Memory destination** — the *unconscious accumulator*. Raw shadow
  material (tensions, avoidances, contradictions, repeated emotional
  vocabulary) accumulates as extracted memories with `layer = shadow`
  and types like `tension` / `pattern`. Patient, non-interpretive,
  collected from the lived stream of conversations. Mostly already in
  our schema; needs sharper extraction discipline (CV7.E3) to actually
  populate.
- **Structural layer** — the *holding-and-surfacing function*. A `shadow`
  layer in the `identity` table, peer to `self` and `ego`. Holds
  *consolidated, ready-to-surface* shadow observations. Composes into
  the prompt under its own conditions. The therapist persona's existing
  "Shadow Profile — Big Five Grounding" section is already a working
  example of structural shadow content: distilled, framed as observation
  with a holding question, ready to be brought to bear when conditions
  invite it.
- **Consolidation as integration** — the bridge between the two. Raw
  shadow memories cluster, get reviewed (manually first), and the ones
  that prove themselves through repetition or significance get distilled
  into structural shadow content. Raw memories don't disappear; they
  remain as provenance. This is the operation Jung called integration,
  and it is the central shadow operation in our system, not a memory
  hygiene step.

Three constraints on how the system holds and surfaces shadow material,
each with direct architectural implications:

**Containment before surfacing.** Not all shadow material is ready to be
brought to consciousness. Material accumulates, gets watched, but is not
pushed into awareness until conditions support it. Shadow content needs
a **readiness state**: `observed` (raw extracted) → `candidate`
(consolidated, awaiting review) → `surfaced` (presented, awaiting
response) → `acknowledged` (accepted by the user) → `integrated`
(promoted into ego/self via identity update). Only `acknowledged` and
higher compose structurally. Without this gradation, the layer either
over-surfaces (constant accusation) or under-surfaces (becomes inert).
This is one new column on the memories table plus a small set of state
transition operations.

**Surfacing as reflection, not verdict.** When shadow content composes,
it composes as observation with provenance ("this has come up three
times: in the conversation about X, the journal entry about Y, the
decision about Z"), not as conclusion ("you avoid vulnerability"). The
composition rule for the shadow layer is different from the composition
rule for self or ego — it requires evidence and grounding in specific
lived material, not just identity content. The therapist persona's
rule — *the mirror does not accuse, it reflects* — lives in the
surfacing logic, not just in tone.

**Asymmetric activation.** Shadow does **not** compose on every
identity-touching turn. Reception needs its own axis for shadow —
`touches_shadow` (or richer: `shadow_evidence_present`) — with stricter
activation conditions than `touches_identity`. The signal: avoidance
dressed as decision, repeated language without resolution, a question
circled without being asked, a value stated against an observed pattern.
This is not magic; it is a periodic and per-turn pass over the
structural shadow layer's content matched against the current message
and recent context. Conservative default (`false`), evidence threshold
required to flip true.

**The asymmetry is the design's center.** Self holds essence. Ego holds
operational identity. Both compose freely because they are *what the
user identifies with*. Shadow holds what the user *does not identify
with* — and the rule for surfacing what someone does not identify with
is fundamentally different from the rule for surfacing what they do.
Modeling shadow as just another peer layer in a symmetric scheme would
miss this. Shadow is a layer, but not a layer like the others. It has
its own composition logic, its own surfacing thresholds, its own
readiness states, its own promotion mechanism.

The deepest architectural question this leaves open — *what determines
that raw shadow material is ready to move from destination to structural
layer?* (auto by repetition count, manual by user acknowledgment,
hybrid) — is the moment of integration itself. It is the single
highest-leverage decision in CV7.E4 and is parked as a planning-pass
question for E4.S3 / E4.S4.

### 5.6 Observability before optimization

Almost every production memory system that worked started with logging. You
cannot tune what you cannot see. This is also Alisson's CV1.E8 instinct.

For us specifically: we have no answer today to "what was the last
extraction prompt's response on conversation X?" beyond rerunning it. A
single `llm_calls` table fixes that and unlocks everything downstream
(eval fixtures, prompt diffing, regression detection).

---

## 6. Proposed shape for CV7

I'm proposing CV7 as **four epics**, ordered by dependency. Numbers are
illustrative; the planning pass will firm them up.

### Theme map

| Theme | What it solves | Inspired by |
|---|---|---|
| Observability | "We can't tune what we can't see." | Alisson CV1.E8 + field |
| Response pipeline | "Every token in the prompt earns its place." | Alisson CV1.E7 |
| Extraction quality | "What we remember is signal, not noise." | Field state of the art |
| Memory depth | "The mirror grows over time, not just remembers." | Memory taxonomy + Jungian |

### CV7.E1 — Pipeline Observability & Evals

**Why first:** every other CV7 story changes LLM behavior. Without
observability and a regression net, we tune blind.

- **S1 — `llm_calls` log table.** One row per LLM call across roles
  (`extraction`, `journal_classify`, `task_extraction`, `week_plan`,
  `routing` if/when we add it). Records `role, model, prompt, response,
  tokens_in, tokens_out, latency_ms, cost_usd, session_id, conversation_id,
  memory_id (if applicable), created_at`. Behind an env flag
  (`MEMORY_LOG_LLM_CALLS=1`) so it doesn't always pay storage cost.
- **S2 — Evals harness.** A `evals/` tree separate from `tests/`. First
  eval: `extraction.py` — fixed conversation transcripts with expected
  memory shapes (type, layer, presence of certain keywords in title/content).
  Second eval: `journey-detection.py`. `uv run python -m memory eval <name>`
  exits non-zero below threshold.
- **S3 — `python -m memory inspect` improvements.** A small CLI that reads
  the `llm_calls` table for a given conversation/session and renders the
  pipeline trace. Sets up the loop `change prompt → re-run conversation →
  diff trace → ship`.

### CV7.E2 — Reception & Conditional Composition

**Why before extraction:** if we add a reception step, extraction (and every
other downstream call) gets richer signals to work with. Building extraction
first and then layering reception on top wastes one extraction iteration.

- **S1 — Reception MVP.** Replace `detect_persona/detect_journey` with a
  single LLM classifier call that returns `{personas, journey,
  touches_identity, touches_shadow, mode}`. Mode is optional in v1 —
  start with persona + journey + identity + shadow. `touches_shadow` is
  not the same as `touches_identity` — it requires evidence of
  avoidance, contradiction, or pattern (not just topical depth) and
  defaults conservatively to `false`. Heuristic fallback (current
  detection) on reception failure or empty pools. Eval covers all
  axes from day one.
- **S2 — Conditional layers in `load_mirror_context`.** Today the function
  always loads soul + ego + (persona) + journey + attachments. Make
  `self/soul` and `ego/identity` conditional on `touches_identity`. Make
  attachments conditional on a `needs_attachments` reception signal (or on
  the existing 0.4 cosine threshold being met). Measure token reduction.
- **S3 — Reception-aware persona/journey routing.** Promote reception's
  result to be the source of truth for `mm-mirror`'s active persona and
  journey, demoting the keyword detection to a fallback. Sticky-defaults
  semantics stay (a session's last persona persists), but reception can
  override per-turn when the message clearly belongs elsewhere.
**Deferred from CV7:** the *expression pass* (mode classification +
post-generation form rewrite). Resolved 2026-04-26 — see §8 for the
watch criterion that would bring it back into scope.

The cleanest architectural payoff of CV7.E2 is that the response pipeline
becomes a **named series of steps with typed contracts**, not one big
prompt assembly call. Once that exists, future changes (compaction, topic
shift detection, shadow surfacing) plug in as additional steps without
touching the core.

### CV7.E3 — Extraction Quality

The current extraction prompt is one of the oldest pieces of code in the
mirror and has not been seriously revised since CV0. Two complaints in
recent memories ("Need to Understand Mirror Mind's Internal Mechanics",
"Adopt Mirror-Mind Documentation Style") signal it's time.

- **S1 — Prompt revision.** Rewrite the extraction prompt with explicit
  rules from the field state of the art: prefer fewer high-quality memories
  over many trivial ones; require concrete, standalone content; surface the
  cognitive role distinction (decision vs insight vs pattern); add explicit
  negative examples ("do not extract small talk"). Eval-driven — fixtures
  in `evals/extraction.py` lock the behavior.
- **S2 — Two-pass extraction.** Split into candidate pass + curation pass
  with deduplication against the user's existing memories (compact
  descriptors fed to the curator). Curator decides layer, merges
  near-duplicates, drops trivia. Net: fewer, better memories per
  conversation.
- **S3 — Per-conversation summary alongside memories.** Today extraction
  produces N typed memories. Add a single conversation-level summary
  (3–4 sentences), stored on the conversation row. Used by `mm-recall`
  and as cheap context for memory search reranking. Inspired by Alisson's
  generated layer summaries — a different artifact, same idea: short,
  lossy, optimized for downstream consumption.
- **S4 — Generated descriptors for personas/journeys.** Same pattern as
  S3, applied to identity. Personas/journeys today route by their full
  ego content; routing accuracy goes up when reception reads a curated
  routing-optimized descriptor instead. This is also a prerequisite for
  CV7.E2.S1's reception eval to converge.

### CV7.E4 — Memory Depth: Search, Reinforcement, Shadow

**Why last:** depends on observability (E1) and is meaningfully better
extraction signals (E3) before it pays off.

- **S1 — Hybrid search 2.0.** Add FTS5 (lexical) alongside the existing
  semantic. Implement RRF or weighted fusion. Add MMR/dedupe on top-k.
  Replace the in-process scan with proper indexed retrieval (sqlite-vec or
  similar) so we scale beyond the current "load everything into memory."
  Eval: a probe set of {query, expected_top_3} fixtures.
- **S2 — Reinforcement honest.** Track `last_accessed_at` and decay
  reinforcement; track *use* (memory was injected and the response
  referenced it) separately from *retrieval*. Tune weights with the eval
  harness, not by feel. Investigate per-layer weight overrides
  (`shadow` memories may want higher recency weight; `self` memories may
  want lower). Adds `last_accessed_at` and a separate `use_count` column
  to the memories table; the `readiness_state` column for shadow
  (introduced in S4) lives on the same table, so plan the migration
  shape together even if the stories ship sequentially.
- **S3 — Memory consolidation as integration.** Reframed (per the
  shadow resolution in §5.5): consolidation is not a memory hygiene
  step — it is the central operation that promotes raw extracted
  memories into structural identity content. Manual first: a
  `mm-consolidate` skill that surfaces clusters of similar memories and
  proposes either a merge, a structural shadow promotion (raw
  `tension`/`pattern` memories → a `shadow`-layer entry), or a direct
  identity-layer update (e.g., `ego/behavior`). The user reviews,
  accepts, edits, or rejects. The proposal trail is preserved
  (provenance from raw memories to structural content). Promotion
  advances the readiness state of source memories from `candidate` to
  `acknowledged`. Automatic consolidation is a future step; the manual
  loop is the right place to learn what the promotion mechanism
  actually wants to be — and answering that question is the planning
  pass's most consequential decision for CV7.E4.
- **S4 — Shadow as structural cultivation.** Per §5.5, shadow is both a
  memory destination and a structural layer; this story builds the
  structural side and the surfacing logic. Four pieces:
  (a) **Schema:** add a `shadow` layer to the `identity` table, peer to
  `self` and `ego`; add a `readiness_state` enum column to the memories
  table (`observed | candidate | surfaced | acknowledged | integrated`)
  with `observed` as the default for newly extracted memories.
  (b) **Material accumulation:** sharpen extraction (depends on
  CV7.E3.S1) so `tension`, `pattern`, and avoidance-shaped memories
  actually land in `layer=shadow` instead of being routed to `ego` by
  default.
  (c) **`mm-shadow` periodic pass:** scans recent memories and the
  structural shadow layer, produces *candidate shadow observations*
  (avoidance patterns, recurring vocabulary, value/decision
  contradictions). Surfaces them with provenance (which memories
  support each observation). User accepts, rejects, or refines.
  Accepted observations are written to the `shadow` identity layer; the
  source memories transition to `acknowledged`.
  (d) **Composition rules:** the `shadow` layer composes into the prompt
  *only* when reception's `touches_shadow` axis flips true (E2.S1) AND
  the structural layer has content in `acknowledged`+ state. Composition
  format includes provenance, not bare claims ("this has come up three
  times: ..." not "you avoid X"). Surfacing is rare and grounded by
  design — the corrosion cost of false positives is high.
  See §5.5 for the conceptual derivation.
- **S5 (stretch) — Cross-conversation summaries / "weekly pass."** A
  scheduled or on-demand operation that compresses the last N
  conversations into a small set of high-signal observations, written
  back as memories with clear provenance. This is the agent equivalent
  of sleep / dream consolidation. Honest about being aspirational —
  defer if E4.S1–S4 don't make it cheap.

### Sequencing

```
   ┌──────────────────────────┐
   │ CV7.E1 — Observability   │
   │ (logs + evals)           │  ← unblocks everything
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ CV7.E2 — Reception &     │
   │ Conditional Composition  │  ← richer signals everywhere
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ CV7.E3 — Extraction      │
   │ Quality                  │  ← cleaner memory in
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ CV7.E4 — Memory Depth    │  ← better recall + shadow
   └──────────────────────────┘
```

E1 and E2 can begin in parallel if needed (the eval harness in E1.S2 is
mostly independent of reception), but landing E1.S1 (logging) before any
E2 story is valuable — every reception call is something we'll want to
inspect.

---

## 7. Success metrics

What does "CV7 succeeded" mean? The naive answer — *quality, then speed,
then cost* — is directionally right but doesn't survive contact with
planning. Four distinctions matter.

### 7.1 Means vs ends

"The model receives the most relevant context possible" is **not** a goal —
it's a lever. Treating it as a goal pushes the system toward *more*
context, which contradicts the principle that every token must earn its
place. The right framing is the inverse:

> The model receives the **minimum sufficient** context to produce a
> high-quality response.

Minimum sufficient, not maximum possible. Context is a dial inside the
response-quality goal, not a separate goal.

### 7.2 Truth vs proxy

Response quality has two observation surfaces, with different physics:

| Surface | Cadence | Cost | Role |
|---|---|---|---|
| User-reported ("this was exactly what I needed", "it remembers the right things") | Rare, lagging | Free but sparse | **Ground truth** |
| Eval-measured (probe sets, LLM-as-judge, structural checks) | Continuous | Cents per run | **Proxy** for the truth |

The user's reports are the truth. Evals are the cheap continuous proxy we
build *because* we can't ask the user every turn. CV7's job is to make the
proxy honest — eval scores that move when the user's perception moves.

### 7.3 Optimization vs envelope

Speed and cost are **not** optimization targets. They are envelopes.

- **Latency.** Has two discontinuities — under ~3s reads as instant; above
  ~10s reads as slow; in between, perception scales roughly linearly.
  "As fast as possible" is wrong; *"stay below the perception threshold"*
  is right.
- **Cost.** Every CV7 story honestly *increases* per-turn cost (reception
  adds a call, two-pass extraction roughly doubles extraction, hybrid
  search 2.0 adds query expansion). Stacked, this can 4× per-turn cost.
  If cost is "minimize," each story dies on cost grounds. If cost is
  *"stay inside a budget envelope,"* each story is argued on
  quality-per-dollar inside a known ceiling.

Envelopes give the planning pass clear stop conditions. Optimization
targets create endless tradeoff arguments.

### 7.4 The success statement

**Primary (the truth — measured rarely, gold standard):**
- User reports: *"the response was exactly what I needed."*
- User reports: *"it remembers the right things."*

**Operational (the proxies — measured continuously via the eval harness):**
- Response quality on a held probe set (LLM-as-judge or structural).
- Extraction quality on conversation fixtures.
- Routing accuracy on a probe set (persona, journey, identity-touch).
- Retrieval relevance on query/expected-top-k probe set.

**Constraints (envelopes, not optimization):**
- Per-turn latency ≤ 5s to first token, ≤ 12s to full response.
- Per-turn cost ≤ a budget to be set at planning time (suggested: ~\$0.05).
- Memory storage growth bounded (consolidation prevents unbounded bloat).

**Anti-goal (named explicitly, so the system doesn't drift toward it):**
- The mirror loads more context "to be safe."

**CV7 succeeded when:**

> At end of CV7, operational eval scores are higher than baseline,
> user-reported satisfaction is at least as good as today, and per-turn
> latency and cost stay inside their envelopes.

This is the metric the eval harness in CV7.E1 must be built to measure.
Baseline scores are taken before E2 ships; deltas are read against that
baseline at each story close-out.

---

## 8. Things explicitly *out* of CV7 in this draft

Naming them is part of the proposal — to keep the CV honest in scope.

- **Topic-shift detection / auto-session-boundaries.** Alisson plans this
  in CV1.E3.S1; for us it requires a stable reception layer first and is
  better treated as its own CV (proactive mirror).
- **Compaction / context-window-aware prompt assembly.** Same — depends on
  reception + observability, deserves its own arc.
- **Multi-persona per turn (Alisson's CV1.E7.S5).** Conceptually compatible
  with our routing model but the UX implications (persona signature, color
  bar in the bubble) belong to a UI-flavored CV, not Intelligence Depth.
- **Self-construction (Alisson's premise P8).** Not in CV7. Mentioned only
  to say so.
- **Server / multi-user runtime.** Out of scope for CV7 — this is mirror's
  identity at the runtime level, not at the intelligence level.

### 8.1 Expression pass and `mode` — deferred, watched

*Resolved 2026-04-26 (Q3).* Reception in CV7.E2.S1 returns four axes
(`personas, journey, touches_identity, touches_shadow`) — not five. The
`mode` axis (conversational / compositional / essayistic) and the
post-generation **expression pass** that Alisson built in his CV1.E7.S1
are explicitly **deferred from CV7**.

**Why deferred.** The expression pass solves a real problem
(*proportionality* — short messages getting back essays, casual asks
getting back lectures). Alisson built it because the corrosion was
actively felt in his use. We do not have evidence yet that the same
corrosion is among our top complaints, and we do not have the
instrumentation (CV7.E1's eval harness) to measure it honestly. Building
the cure before measuring the disease is the over-engineering this CV is
trying to avoid.

**Watch criterion — what would bring it back into scope.** Once CV7.E1
lands, add a *proportionality* probe to the eval harness: a probe set
of short, casual, lived-in user messages with the expectation that
responses stay short and proportional. If responses systematically
over-shape (essays for one-line messages, lectures for casual asks),
the expression pass earns its way back into the roadmap as a focused
mini-CV or a tight epic in CV8. Until that signal lands, we ship
without it.

**Anti-trap.** "Stamp `mode` on the assistant message now, build the
expression pass later" is the seductive middle path. Reject it. A mode
stamp without a downstream consumer is dead metadata that will drift
out of awareness and never get the form benefit. When we revisit this,
we revisit *both* axes together — classification and consumption — or
neither.

---

## 9. Open questions for the planning pass

1. **Reception model choice.** Alisson uses Gemini 2.5 Flash with
   `reasoning: "minimal"` and a 5s timeout. We currently use the same
   model for extraction. Do we run reception on the same model, or
   intentionally pick a smaller/faster one (Haiku 4.5, gemini-2.5-flash-
   lite)? An eval comparing both at parity prompt is a one-day spike.
2. **Where do generated descriptors live?** Alisson stores them on the
   identity row (`identity.summary`). We currently have no analogous
   field. Do we add `summary` to identity rows, or store descriptors
   in a sidecar table? The first is simpler; the second keeps a clean
   migration path for "generate a descriptor from any kind of content."
3. ~~**Is "mode" (conversational/compositional/essayistic) worth
   porting?**~~ **Resolved** 2026-04-26 — deferred from CV7. See §8.1
   for the watch criterion that would bring it back.
4. ~~**Shadow as a layer vs shadow as a memory type.**~~ **Resolved**
   2026-04-26 in a Mirror Mode session with the therapist persona.
   Shadow is **both** a structural layer and a memory destination, with
   a consolidation pipeline between them and a readiness-state model on
   memories. See §5.5 for the canonical framing and E4.S3 / E4.S4 for
   the architectural consequences. The remaining sub-question — *the
   promotion mechanism* (auto by repetition, manual by acknowledgment,
   hybrid) — is parked for the E4.S3 planning pass; it is the single
   highest-leverage decision left in CV7.E4.
5. **Per-turn cost envelope — what's the actual ceiling?** Section 7
   commits to cost-as-envelope but leaves the number open. Suggested
   \$0.05/turn as a starting point; the planning pass should confirm
   against current per-turn cost data and the budget Vinícius is
   willing to spend monthly.

---

## 10. References

**This repo:**
- Current extraction: `src/memory/intelligence/extraction.py`
- Current search: `src/memory/intelligence/search.py`
- Current routing: `src/memory/client.py` (`detect_persona`, `detect_journey`)
- Mirror context loader: `src/memory/skills/mirror.py` (`load_mirror_context`)
- CV7 index: `docs/project/roadmap/cv7-intelligence-depth/index.md`

**Alisson's repo (`~/dev/workspace/mirror-mind`):**
- Memory taxonomy: `docs/product/memory-taxonomy.md`
- Memory map: `docs/product/memory-map.md`
- Prompt composition (canonical): `docs/product/prompt-composition/index.md`
- Reception: `server/reception.ts`
- Composition: `server/identity.ts`
- Expression pass: `server/expression.ts`
- Generated summaries: `server/summary.ts`
- Evals: `evals/`, `docs/process/evals.md`
- CV1.E7 (Response Intelligence): `docs/project/roadmap/cv1-depth/cv1-e7-response-intelligence/index.md`
- CV1.E8 (Observability): `docs/project/roadmap/cv1-depth/cv1-e8-pipeline-observability-eval/index.md`

---

**See also:** [CV7 index](index.md) · [Briefing](../../briefing.md) · [Decisions](../../decisions.md)
