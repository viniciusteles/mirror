[< CV4.E5 Legacy Migration into User Home](../index.md)

# CV4.E5.S2 — Plan: Legacy schema and vocabulary translation into `memory.db`

## What and Why

CV4.E5.S1 defines the migration source/target contract and safety rules. This
story plans the actual translation work needed to move Portuguese-era persisted
data into the current English model.

This is the closest planning story to the original technical migration idea:
- `memoria.db` → `memory.db`
- `travessia` → `journey`
- `travessia_id` → `journey_id`
- `caminho` → `journey_path`
- related schema/index/value translation

But the work is broader than renaming strings. We need to define:
- what schema elements are translated
- what data values are translated
- what stays semantically identical
- how to validate correctness after translation
- how to treat partially migrated or mixed-state legacy inputs safely

---

## Translation Scope

### Primary database/file vocabulary
- `memoria.db` → target `memory.db`

### Schema-level translation targets
Based on the earlier English migration plan, important targets include:
- `conversations.travessia` → `conversations.journey`
- `memories.travessia` → `memories.journey`
- `tasks.travessia` → `tasks.journey`
- `attachments.travessia_id` → `attachments.journey_id`
- indexes such as `idx_memories_travessia` → `idx_memories_journey`
- identity layer value `travessia` → `journey`
- identity layer value `caminho` → `journey_path`

### YAML / identity data vocabulary relevant to migration
- `travessia_id` → `journey_id`
- legacy journey-layer content and metadata aligned to English naming

---

## Proposed Translation Principles

### 1. Translate semantics, not just spelling

The migration must preserve meaning. A mechanical rename that breaks
relationships, indexes, or identity-layer semantics is not acceptable.

### 2. Preserve data whenever possible

Existing records, associations, and content should survive translation intact,
except where the name/value must change to fit the English model.

### 3. Characterize before rewriting

Tests/fixtures should prove what a realistic legacy source looks like before the
translation logic is finalized.

### 4. Treat mixed/partial states explicitly

Legacy inputs may not all be perfectly clean Portuguese-era snapshots. Some may
already be partially migrated. The translation plan should decide whether to:
- support mixed states explicitly
- reject them clearly
- or support only a narrow known source shape

---

## Recommended Direction

- use explicit mapping tables for schema, field, and value translation
- preserve relationships and row counts as verification anchors
- validate translated indexes/columns/layers, not only raw row presence
- support known legacy source states deliberately, not by accident
- keep translation logic separate from source/destination safety logic

---

## Candidate Mapping Areas

### Table/column/value mappings
A central mapping layer should likely cover:
- database/file names
- table/column names
- identity layer names
- YAML key names where relevant
- index names

### Relationship-sensitive areas
Particular care is needed where naming changes affect joins, lookups, or
foreign-key-style references:
- attachments and `journey_id`
- conversation/memory/task journey linkage
- identity layer retrieval and filtering

### Non-goal for this story
This story does not implement the migration tool. It defines the translation
plan and verification shape.

---

## Questions This Story Should Settle

1. Which legacy source states are officially supported by the migration path?
2. Should mixed Portuguese/English legacy states be accepted, normalized, or rejected?
3. What translation mapping should be centralized vs. encoded in migration steps directly?
4. What verification signals are mandatory after translation (row counts, indexes, layer values, sample retrievals)?
5. Which existing English-migration docs/tests can be reused as characterization input?

---

## Deliverable

This story should produce planning/docs that define:
- the schema/value translation scope
- the translation principles and mapping areas
- the verification shape for proving the migrated target is correct

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Mechanical rename illusion
A rename can appear successful while relationships or filters are broken underneath.

### 2. Mixed-state ambiguity
If partially migrated sources are not handled explicitly, migration behavior may become unpredictable.

### 3. Verification too shallow
Checking only that the destination DB exists is not enough. We need semantic verification.

### 4. Overcoupling translation and safety logic
Source/destination safety rules and schema translation rules should remain conceptually separate.

---

## Follow-on Work Enabled

Once S2 is accepted, later stories can plan:
- concrete migration implementation steps
- characterization fixtures/tests for Portuguese-era databases
- validation/reporting logic for translated outputs
- explicit handling strategy for mixed-state legacy inputs
