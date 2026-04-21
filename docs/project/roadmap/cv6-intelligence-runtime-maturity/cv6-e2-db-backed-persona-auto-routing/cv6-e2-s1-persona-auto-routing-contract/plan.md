[< CV6.E2 Persona Auto-Routing from Database Metadata](../index.md)

# CV6.E2.S1 — Plan: Define the persona auto-routing contract and scoring rules

## What and Why

Mirror Mind already supports journey detection from the query, but persona
selection still depends on explicit persona input or sticky defaults. That means
Mirror Mode does not yet honor the routing model described in `CLAUDE.md` as a
runtime capability.

Once CV6.E1 makes runtime persona metadata database-backed, this story defines
how persona auto-routing should actually work.

---

## Problem to Solve

Current persona resolution in `src/memory/skills/mirror.py` effectively follows:
1. explicit persona
2. session sticky persona
3. global sticky persona
4. no persona detection

That is incomplete. The system needs a contract for:
- when persona auto-detection runs
- what metadata it uses
- how multiple matches are scored
- how explicit/sticky state interacts with detection
- how to fall back cleanly when no persona is a good match

---

## Proposed Routing Contract

### Runtime source of truth

Persona detection reads persona routing metadata from the database only.

### Resolution order

Recommended precedence:
1. explicit persona argument
2. current-session sticky persona
3. global sticky persona
4. auto-detected persona from the query using DB-backed metadata
5. ego/no-persona fallback

This preserves operator control and conversational continuity while still adding
true runtime auto-routing when no persona is already established.

### Detection inputs

At minimum, auto-routing should consider:
- `routing_keywords`
- optionally persona `name`
- optionally persona `description`

The first implementation should prioritize clarity and inspectability over
semantic complexity.

### Matching direction

Recommended first-cut scoring:
- normalize query and keywords to lowercase
- tokenize simply and predictably
- count keyword hits per persona
- prefer exact lexical matches over fuzzy magic
- return ranked candidates, not only one opaque winner

A semantic or embedding-based persona router can be considered later, but it
should not be required for the first DB-backed implementation.

### No-match behavior

If no persona crosses a clear threshold, Mirror Mode should respond from ego
without a persona rather than forcing a weak match.

### Debuggability

The detected persona and enough supporting signal should be inspectable in tests
and, where appropriate, in CLI/runtime output.

---

## Questions This Story Should Settle

1. What minimum score or threshold constitutes a persona match?
2. Should multiple keyword hits across personas produce a ranked list or a tie-break rule?
3. Should description/name contribute to scoring in the first version or only keywords?
4. How should auto-detection interact with future session-aware persona switching?
5. What CLI/debug output is appropriate without cluttering normal usage?

---

## Recommended Direction

- keep precedence simple: explicit > sticky > detected > ego
- make the first version keyword-based and deterministic
- return ranked candidates internally even if only the top persona is selected
- keep scoring logic small enough to test thoroughly
- avoid any runtime dependency on YAML files or repo-side persona definitions

---

## Deliverable

This story should produce planning/docs that define:
- the persona auto-routing precedence model
- the first scoring/matching rules
- the no-match fallback behavior
- the debug/inspection expectations for routing results

Implementation belongs to CV6.E2.S2.

---

## Risks and Design Concerns

### 1. Hidden magic
If persona routing becomes too fuzzy too early, debugging will be painful.

### 2. Overriding conversational continuity
Auto-detection should not casually displace an already established persona.

### 3. Weak-match forcing
A poor heuristic that always picks some persona will degrade trust.

### 4. Contract drift from `CLAUDE.md`
The runtime routing model should align with the documented ego-persona model,
not evolve as an unrelated heuristic side channel.

---

## Follow-on Work Enabled

Once S1 is accepted, later stories can implement:
- database-backed persona detection helpers
- Mirror Mode resolution changes in `src/memory/skills/mirror.py`
- unit/integration coverage for explicit, sticky, detected, and fallback cases
- CLI inspection of detected persona candidates where useful
