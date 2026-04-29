[< CV8.E1 Gemini CLI Runtime Spike](../index.md)

# CV8.E1.S1 — Inspect Gemini CLI Capabilities

**Status:** Done
**Epic:** CV8.E1 — Gemini CLI Runtime Spike
**Type:** Spike / discovery

---

## Outcome

Determine what Gemini CLI exposes as a runtime surface and gather enough evidence
to map it against the Mirror Mind runtime contract.

This story does **not** implement Gemini CLI support. It only inspects, probes,
and documents Gemini CLI capabilities so the later implementation plan is
grounded in facts rather than assumptions.

---

## Questions To Answer

- Does Gemini CLI support project-local instructions?
- Does Gemini CLI support custom commands, slash commands, skills, or equivalent
  command files?
- Does Gemini CLI support lifecycle hooks?
  - session start
  - before user prompt / before agent
  - before model request
  - after model response
  - after assistant response / after agent
  - session end
- Does Gemini CLI expose a stable session id?
- Does Gemini CLI expose transcript files?
- Can Gemini CLI inject context before the model responds?
- Can Gemini CLI run shell commands automatically from runtime events or custom
  commands?
- Can Gemini CLI pass prompt and assistant-response text into those commands?

---

## Done Condition

- Gemini CLI installation and version are identified, or absence is documented
- Gemini CLI local configuration/project-file conventions are identified
- Gemini CLI command/customization surface is identified
- Gemini CLI lifecycle/hook capabilities are identified
- Gemini CLI prompt/assistant capture capabilities are identified
- Gemini CLI session id or fallback strategy is identified
- Gemini CLI context-injection capability is classified
- findings are recorded in `plan.md`
- enough evidence exists to proceed to CV8.E2 implementation

---

## Non-Goals

- no Gemini CLI adapter files
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
