[< Docs](../index.md)

# Development Guide

How we work. This is a working agreement, not a style guide. It encodes what
we have learned about what makes sessions productive.

---

## The Model

**The user is the navigator. The agent is the driver.**

The navigator sets direction, raises concerns, and spots the larger pattern.
The driver implements — but also speaks up when something looks wrong at the
wheel. Constant dialogue. The driver does not disappear into implementation.

---

## Before Writing Code

For non-trivial work, design first:

1. Read the relevant code — understand what exists before proposing what is new
2. Design the approach — consider the trade-offs
3. Present the plan and get confirmation
4. Only then implement

The plan becomes the story doc (`plan.md`). If the story does not have a plan
doc, it is either trivial (a typo fix, a one-line change) or the design step
was skipped.

**The driver asks clarifying questions before writing code.** If the direction
is unclear, stop and ask rather than make assumptions.

---

## During Implementation

- Flag design issues proactively — coupling, naming, missing tests, unnecessary
  complexity — even when not asked
- Narrate key decisions and flag alternatives at meaningful checkpoints
- Do not grow scope during implementation; record scope additions for the next story
- TDD: write tests that fail, then make them pass

---

## Verification Checklist

Every story ends with:

```bash
pytest                              # all tests pass
ruff check src/ tests/              # no lint violations
ruff format --check src/ tests/     # no formatting issues
pyright src/memory                  # no type errors
git diff --check                    # no trailing whitespace
```

For stories that touch runtime behavior, also run an isolated smoke test with
temporary `HOME` and `MEMORY_DIR` to confirm no production database is touched.

---

## Commits

- One concern per commit
- Descriptive English message — explain why, not just what
- No `WIP`, no `fix stuff`, no Portuguese names
- Never skip hooks (`--no-verify`)
- Never amend a pushed commit

### After Push

A story is not operationally done until the pushed GitHub Actions run is green.

Required procedure:

1. inspect the new run with GitHub CLI (`gh`)
2. wait for the workflow to finish
3. if CI fails, inspect the failing job/logs
4. fix the problem
5. push again
6. confirm CI is green before moving on

Example of a good commit message:

```
Extract mirror skill logic into src/memory/skills/mirror.py

Move the load/log/context-only logic from .claude/skills/mm:mirror/run.py
into an importable module so Pi skills can call the same implementation.
```

---

## Docs

- Update docs in the same commit as the code change they describe
- When a story is done, mark it ✅ in the epic index and add an entry to the worklog
- If refactoring was done or deferred, record it in `refactoring.md` under the story folder
- Breadcrumbs and "See also" links: update them when you add or rename docs

---

## Story Lifecycle

1. Story appears in the epic index with status `—`
2. Story gets `index.md` (outcome) + `plan.md` (design) + `test-guide.md` (verification)
3. Driver and navigator review the plan
4. Implementation begins
5. Verification checklist passes
6. Story marked ✅ in epic index
7. Worklog entry added
8. Commit(s) with descriptive messages
9. Push when the user asks

---

## What We Have Learned

**The process self-documents.** Session logs, story docs, and the decisions file
together reconstruct the full history without needing to ask anyone.

**Small stories validate faster.** A story that cannot be verified end-to-end in
one session is too large. Split it before starting implementation.

**Docs are part of the deliverable.** A story is not done if the code works but
the story index, plan, and worklog are not updated.

**The smoke test pattern is reusable.** Isolated `HOME` + `MEMORY_DIR` + empty-string
env vars prevents `.env` from repopulating paths. Use this pattern for any
end-to-end validation that touches storage.

**Design debt is in-cycle work.** Ask at the end of every story: what did we
accumulate? What can we clean now? Deferring everything creates invisible load.

**Split by ownership, not by convenience.** When a skill mixes DB access with filesystem reading, split it: CLI for DB, agent for filesystem. The agent's native file tools are already excellent — duplicating them in Python is waste, not thoroughness. This principle eliminated 23 run.py files in CV3.E4.

---

---

## Evals

Evals live in `evals/`, separate from `tests/`. They hit real LLM APIs, cost a
few cents per run, and are non-deterministic. **Do not add them to CI.**

The failure semantics are different from tests: a failing eval means *behavior
drifted*, not *code broke*. A passing eval does not mean code is correct —
it means the LLM is behaving within the expected envelope for that probe set.

**When to run:**
- Before changing any prompt in `src/memory/intelligence/prompts.py`
- Before shipping any change that touches extraction, routing, or reception logic
- After a model change in `src/memory/config.py`
- Before closing any CV7 story that modifies LLM behavior

**How to run:**

```bash
uv run python -m memory eval extraction
uv run python -m memory eval routing          # available after CV7.E1.S3
uv run python -m memory eval proportionality  # available after CV7.E1.S3
```

Exit code 0 means the probe score met the threshold. Exit code 1 means it did
not — investigate which probes failed before shipping.

**How to add a new eval:**

1. Create `evals/<name>.py`
2. Define `PROBES: list[EvalProbe]` and `THRESHOLD: float`
3. Each probe has an `id`, a `description`, and a `run() -> tuple[bool, str]`
   callable that returns `(passed, notes)`
4. The `run()` function calls real intelligence functions — no mocking
5. Document the intent of each probe in its `description`

Example:

```python
from evals.types import EvalProbe

THRESHOLD = 0.8

def _my_probe() -> tuple[bool, str]:
    result = some_intelligence_function(inputs)
    passed = meets_expected_shape(result)
    return passed, f"{len(result)} items returned"

PROBES = [
    EvalProbe(id="my-case", description="...", run=_my_probe),
]
```

**See also:** [Principles](../product/principles.md) · [Worklog](worklog.md)
