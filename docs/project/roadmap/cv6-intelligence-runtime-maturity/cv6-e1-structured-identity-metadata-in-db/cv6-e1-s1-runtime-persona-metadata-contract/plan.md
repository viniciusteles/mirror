[< CV6.E1 Structured Identity Metadata in the Database](../index.md)

# CV6.E1.S1 — Plan: Define the runtime persona metadata contract

## What and Why

Mirror Mind already treats the database as the runtime source of truth for
identity content. But for personas, only the prompt body is preserved. Important
runtime-relevant fields such as `routing_keywords` are lost during seeding.

That creates an architectural gap:
- persona prompt text is DB-backed
- persona routing metadata remains trapped in YAML
- runtime cannot perform persona auto-routing from database state alone

This story defines the contract that closes that gap.

---

## Problem to Solve

Today `src/memory/cli/seed.py` reads persona YAML and stores only a combined
content blob (primarily `system_prompt` plus optional `briefing`). The runtime
therefore loses structured persona facts such as:

- `name`
- `inherits_from`
- `description`
- `routing_keywords`
- `default_model`
- other future metadata needed for inspection or routing

If Mirror Mind is to onboard other users cleanly, the runtime should not need to
re-open seed YAML files to recover those facts.

---

## Proposed Contract

### Source of runtime truth

Runtime persona metadata must be read from the database, not from the YAML files
that were used as seed input.

### Metadata shape

At minimum, the runtime persona metadata contract should preserve:
- `persona_id`
- `name`
- `inherits_from`
- `description`
- `routing_keywords`
- `default_model`
- `version`

Optional fields may be added later, but the contract should be clear about which
ones are runtime-relevant now.

### Prompt content remains distinct

The persona's prompt body used for mirror-context injection should remain
conceptually distinct from its structured metadata.

That means the design should avoid treating one opaque Markdown blob as the only
representation of a persona.

### Preferred storage direction

The recommended direction is to keep identity rows database-backed while adding a
structured metadata representation that runtime code can query directly.

Candidate approaches to evaluate:
1. extend identity rows with a `metadata` JSON field
2. add a dedicated table for persona definitions/metadata

This story should recommend one direction explicitly, with rationale.

---

## Questions This Story Should Settle

1. What persona fields are mandatory runtime metadata in CV6?
2. Should metadata live in `identity` rows or in a dedicated typed table?
3. How should `routing_keywords` be represented and validated?
4. How should `mem.get_identity(...)` and related APIs evolve, if at all?
5. What CLI/inspection behavior should expose persona metadata for debugging?
6. How should the design preserve backward compatibility for already-seeded databases?

---

## Recommended Direction

- preserve persona prompt content and persona metadata as separate concepts
- make database metadata the sole runtime source for routing-relevant persona facts
- choose a storage model that is easy to inspect, migrate, and query from runtime code
- avoid any runtime fallback that re-reads seed YAML files to recover metadata
- make the metadata contract explicit enough to support CV6.E2 persona auto-routing

---

## Deliverable

This story should produce planning/docs that define:
- the runtime persona metadata contract
- the storage direction for that metadata in the database
- the minimum fields required for persona routing and inspection
- the migration/compatibility direction for existing databases

Implementation belongs to CV6.E1.S2 and CV6.E2.

---

## Risks and Design Concerns

### 1. Opaque-content trap
If persona metadata remains embedded only in freeform prompt content, runtime
routing and inspection will stay brittle.

### 2. YAML leakage into runtime
If runtime code is allowed to recover metadata by reading seed YAML, the DB
stops being the real source of truth.

### 3. Over-design too early
We need a structured model strong enough for routing without designing an entire
plugin/identity platform prematurely.

### 4. Migration friction
Already-seeded databases should gain the new metadata model through a clean,
explicit migration path.

---

## Follow-on Work Enabled

Once S1 is accepted, later stories can implement:
- database schema changes or metadata persistence changes
- seeding updates for persona metadata
- CLI inspection of DB-backed persona metadata
- persona auto-routing from database state only
