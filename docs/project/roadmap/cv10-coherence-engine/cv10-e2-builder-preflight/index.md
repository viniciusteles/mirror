[< CV10](../index.md)

# CV10.E2 — Builder Preflight

**Status:** Planned
**User-visible outcome:** Builder Mode automatically loads coherence state for a
journey's project path and surfaces blocking UoCs before implementation work.

---

## Scope

Integrate the coherence core into the existing Builder lifecycle.

When running:

```bash
uv run python -m memory build load <journey>
```

Builder should:

- resolve `project_path` as it does today
- evaluate base-lens UoCs when `project_path` exists
- write or refresh `docs/coherence/index.md`
- print a concise Coherence section in the Builder context
- preserve the existing final `project_path=<path>` contract

---

## Done Condition

CV10.E2 is done when:

- `/mm-build <journey>` includes a coherence summary in the loaded context
- blocking UoCs are visible to the agent before implementation work
- journeys without `project_path` continue to load normally
- Builder behavior stays compatible across Pi, Gemini CLI, Codex, and Claude Code skill surfaces

---

## See also

- [Coherence Runtime Specification](../../../../product/specs/coherence-runtime/index.md)
- [CV10.E1 Coherence Core](../cv10-e1-coherence-core/index.md)
