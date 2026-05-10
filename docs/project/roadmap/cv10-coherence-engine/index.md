[< Roadmap](../index.md)

# CV10 — Coherence Engine

**Status:** Planned
**Goal:** Make coherence a natural Builder lifecycle capability, so Mirror can
surface and govern gaps between observed project state and active lenses without
requiring the user to invoke a separate coherence command.

---

## What This Is

CV10 introduces Units of Coherence (UoCs) as a generic Mirror capability. A UoC
compares what is true now with what an active lens says should be true, then
makes any gap visible for judgment.

The first product expression is Maestro: a doing-first software-development
experience where Builder is governed by coherence and software lenses. Maestro
is not a competing mode or command. It is a productized Builder configuration
powered by Mirror Core.

---

## Scope

CV10 includes:

- a generic UoC model in the Mirror Python core
- a base lens with the smallest project-level UoCs
- automatic Builder preflight on activation
- project-visible coherence docs under `docs/coherence/`
- a post-change coherence refresh protocol
- lens configuration for future XP, DDD, and Kanban lenses

CV10 does not include full localization or audience modes. It must keep the
coherence model compatible with both, but those are Mirror-wide capabilities
planned separately in CV11 and CV12.

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|----------------------|--------|
| [CV10.E1](cv10-e1-coherence-core/index.md) | Coherence Core | Mirror can evaluate base UoCs for a project path and write a coherence index | 🟡 Planned |
| [CV10.E2](cv10-e2-builder-preflight/index.md) | Builder Preflight | Builder Mode automatically loads coherence state when a journey starts | 🟡 Planned |
| CV10.E3 | Builder Postflight | Builder refreshes coherence after meaningful project changes | 🟡 Planned |
| CV10.E4 | Lens Configuration | Journeys can select active lenses such as base, XP, DDD, or Kanban | 🟡 Planned |

---

## Done Condition

CV10 is done when:

- `/mm-build <journey>` loads coherence state automatically for journeys with a project path.
- Blocking UoCs are surfaced before implementation work.
- Non-blocking UoCs remain visible without blocking exploration.
- `docs/coherence/index.md` is created or refreshed in the target project.
- The base lens supports at least `project.working_name` and `project.git_repository`.
- The runtime contract remains compatible across Pi, Claude Code, Gemini CLI, and Codex skill surfaces.
- The UoC model separates semantic ids from human-facing text.

---

## Sequencing

```text
E1 Coherence Core
  └── E2 Builder Preflight
        └── E3 Builder Postflight
              └── E4 Lens Configuration
```

---

## See also

- [Coherence as Product Architecture](../../../product/envisioning/index.md)
- [Coherence Runtime Specification](../../../product/specs/coherence-runtime/index.md)
- [CV9 Mirror Mind 1.0](../cv9-mirror-1-0/index.md)
