[< CV3 Pi Skill Parity](../index.md)

# CV3.E3 — Pi Intelligence Skills

**Epic:** `mm:consult` and, historically, `mm:review-copy` available on Pi
**Status:** ✅ Done  
**Can run parallel with:** CV3.E2 once CV3.E1 is done

---

## What This Is

Two Claude Code skills involve multi-LLM calls and structured output. They are
more complex than simple CLI dispatch and warrant their own epic.

**mm:consult** — sends a query to multiple LLMs via OpenRouter and returns
their responses for comparison. Logic lives in `.claude/skills/mm:consult/run.py`
and `src/memory/intelligence/llm_router.py`.

**mm:review-copy** — sends copy to multiple LLMs, collects structured reviews,
and generates an HTML report. At the time of CV3, it was shipped as a Pi skill
for parity with Claude's model-driven workflow.

From the later CV6 perspective, this capability is best understood as a
**reference extension example**, not a permanent core framework feature. The
repo-local Pi skill has since been removed and replaced by the external
`ext-review-copy` path.

---

## Done Condition

- `mm-consult` Pi skill exists, dispatches to `python -m memory consult`
- historically, `mm-review-copy` existed with a SKILL.md describing the workflow
- the skill could later be reclassified as a reference extension without changing
  the fact that CV3 delivered Pi parity for it at the time
- Both skills produced correct output on Pi at delivery time
- Existing tests pass

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV3.E3.S1 | Add `consult` CLI command and Pi skill wrapper | ✅ |
| CV3.E3.S2 | Add `mm-review-copy` Pi skill (SKILL.md, model-driven) | ✅ |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV3 Pi Skill Parity](../index.md) · [CV3.E2 Pi Skill Wrappers](../cv3-e2-pi-skill-wrappers/index.md)
