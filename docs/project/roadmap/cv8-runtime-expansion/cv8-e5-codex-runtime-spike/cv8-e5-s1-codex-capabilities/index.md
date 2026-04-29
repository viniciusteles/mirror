[< CV8.E1 Codex Runtime Spike](../index.md)

# CV8.E1.S1 — Inspect Codex Capabilities

**Status:** Draft
**Epic:** CV8.E1 — Codex Runtime Spike
**Type:** Spike / discovery

---

## Outcome

Determine what Codex exposes as a runtime surface and gather enough evidence to
map it against the Mirror Mind runtime contract.

This story does **not** implement Codex support. It only inspects, probes, and
documents Codex capabilities so the later implementation plan is grounded in
facts rather than assumptions.

---

## Questions To Answer

- Does Codex support project-local instructions?
- Does Codex support custom commands, slash commands, skills, or equivalent
  command files?
- Does Codex support lifecycle hooks?
  - session start
  - before user prompt
  - after assistant response
  - session end
- Does Codex expose a stable session id?
- Does Codex expose transcript files?
- Can Codex inject context before the model responds?
- Can Codex run shell commands automatically from runtime events or custom
  commands?
- Can Codex pass prompt and assistant-response text into those commands?

---

## Done Condition

- Codex installation and version are identified, or absence is documented
- Codex local configuration/project-file conventions are identified
- Codex command/customization surface is identified
- Codex lifecycle/hook capabilities are identified
- Codex prompt/assistant capture capabilities are identified
- Codex session id or fallback strategy is identified
- Codex context-injection capability is classified
- findings are recorded in `plan.md`
- enough evidence exists to proceed to CV8.E1.S2 lifecycle mapping

---

## Non-Goals

- no Codex adapter files
- no runtime command surface implementation
- no changes to Python runtime behavior
- no schema changes
- no public docs update beyond this story documentation

---

## See also

- [Plan](plan.md)
- [Test Guide](test-guide.md)
- [CV8 index](../../index.md)
- [Runtime Interface Contract](../../../../runtime-interface.md)
