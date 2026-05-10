[< Specs](../index.md)

# Coherence Runtime Specification

This specification describes how the coherence engine should integrate with the
Mirror runtime. It is intentionally runtime-level: product framing lives in
[Coherence as Product Architecture](../../envisioning/index.md), while roadmap
execution lives under [CV10 Coherence Engine](../../../project/roadmap/cv10-coherence-engine/index.md).

## Principle

Coherence is a Builder lifecycle capability, not a command-first user flow.

The user should keep saying:

```text
activate Builder Mode for journey X
```

When coherence is enabled for that journey, Builder automatically performs a
preflight check, carries the resulting UoCs in its briefing, and refreshes
coherence after meaningful changes.

## Inputs

A coherence run receives:

```text
journey slug
project_path
active lenses
runtime locale, when localization exists
runtime audience mode, when audience modes exist
```

For CV10, locale and audience mode are compatibility concerns only. Full
localization and audience-mode behavior belong to separate Mirror-wide
capabilities.

## Outputs

A coherence run produces:

```text
CoherenceResult
  journey slug
  project_path
  active lenses
  list of Units of Coherence
  blocking count
  open count
  resolved count
```

It also writes or refreshes:

```text
<project_path>/docs/coherence/index.md
```

The index is project-visible state. It lets the user and future agent sessions
see what is coherent, what is missing, what was deferred, and what was accepted.

## Unit of Coherence

A Unit of Coherence, abbreviated UoC, contains:

```text
semantic_id
stable machine-readable id, for example project.working_name

display_id
human-friendly id, for example UoC-001

scope
project, product, process, story, docs, code, or journey

lens
which lens produced the expectation

severity
blocking, important, optional

status
open, resolved, deferred, accepted

expected_state
what the lens expects

observed_state
what inspection found

gap
why observed state and expected state differ

evidence
facts used to support the observed state

suggested_action
how the gap can be resolved, deferred, or accepted
```

A gap is a request for judgment, not automatically an error.

## Builder activation preflight

When Builder Mode loads a journey with coherence enabled:

```text
1. Load identity, journey context, and Builder persona as today.
2. Resolve project_path as today.
3. Load coherence configuration for the journey.
4. Load active lenses.
5. Inspect project_path.
6. Evaluate UoCs.
7. Write docs/coherence/index.md.
8. Print a Coherence section in the Builder context.
9. Emit project_path as the final line as today.
```

The existing `memory build load <slug>` contract must remain compatible with
current `/mm-build` behavior. The coherence section is additive.

## Builder behavior with UoCs

If blocking UoCs exist, Builder must surface them before implementation work.
The user may resolve, defer, or accept them, but the assistant should not hide
them.

If only non-blocking UoCs exist, Builder may proceed while keeping them visible.
The assistant should use judgment: some important UoCs can be deferred during
exploration, but should reappear before closure.

## Post-change coherence refresh

After meaningful changes, Builder should run a coherence postflight when any of
these are touched:

```text
project docs
roadmap or story docs
source code
tests
configuration
process/status documents
```

The postflight should report:

```text
new UoCs
resolved UoCs
still-open UoCs
changed severity or status
```

CV10 can start with manual postflight inside the assistant instructions. A later
implementation may add hook-based or file-change-aware refresh.

## Persistence

CV10 uses project-visible docs as the first persistence layer:

```text
docs/coherence/index.md
```

Future work may persist UoCs in the memory database for querying across
journeys, historical drift analysis, and consolidation. The first implementation
should not require database persistence to prove the lifecycle.

## Lens configuration

A lens provides UoC rules and rendering metadata. The base lens should include
only the smallest project-level expectations required to validate the engine:

```text
project.working_name
project.git_repository
```

The XP lens can later add story lifecycle, test, refactoring, and documentation
expectations.

## Compatibility with localization and audience modes

CV10 must not hardcode semantics into English prose. It should keep semantic ids
separate from human-facing text so future localization can translate output.

CV10 must not weaken coherence rules for non-technical users. Audience mode may
change explanation depth later, but not what is considered coherent.

## Done condition for first runtime slice

The first runtime slice is done when:

```text
/mm-build <journey>
```

or its equivalent runtime skill:

```text
- loads the journey as before
- resolves project_path as before
- evaluates base-lens UoCs automatically
- writes docs/coherence/index.md under project_path
- injects a concise Coherence section into Builder context
- surfaces blocking UoCs before implementation
- keeps existing Builder behavior compatible
```
