[< Story](index.md)

# Test Guide — CV8.E5.S1 Inspect Codex Capabilities

This is a spike, so verification means the investigation is reproducible and
the evidence is recorded. No Codex runtime implementation should exist after
this story.

---

## 1. Verify docs exist

```bash
test -f docs/project/roadmap/cv8-runtime-expansion/cv8-e1-codex-runtime-spike/cv8-e1-s1-codex-capabilities/index.md
test -f docs/project/roadmap/cv8-runtime-expansion/cv8-e1-codex-runtime-spike/cv8-e1-s1-codex-capabilities/plan.md
test -f docs/project/roadmap/cv8-runtime-expansion/cv8-e1-codex-runtime-spike/cv8-e1-s1-codex-capabilities/test-guide.md
```

Expected: all commands exit `0`.

---

## 2. Verify no implementation files were added

Before closing the spike, inspect the diff:

```bash
git status --short
git diff --stat
```

Expected:

- only story docs are changed during story setup
- later spike notes may update the same docs
- no Codex runtime adapter files exist yet
- no Python runtime behavior changed

---

## 3. Verify Codex installation evidence is recorded

Open `plan.md` and confirm the Evidence Log includes concrete values for:

- Codex installed
- executable path or absence
- version or absence
- docs/sources inspected

Expected: no `TBD` remains in the Installation and Docs/Sources sections after
the spike is complete.

---

## 4. Verify runtime capability evidence is recorded

Open `plan.md` and confirm evidence exists for:

- project-local config
- command surface
- lifecycle hooks
- session id
- prompt/assistant capture
- transcript/log availability
- context injection

Expected: every section contains findings and, where appropriate, explicit
"not supported" or "not found" statements.

---

## 5. Verify next story can proceed

Confirm `plan.md` has an initial Codex target parity level:

```text
Initial Codex target parity: L0/L1/L2/L3/L4
```

Expected: one level is selected with rationale.

---

## 6. Standard repository checks

For docs-only changes:

```bash
git diff --check
```

Expected: no whitespace errors.

Full test suite is not required for this docs-only spike setup unless later
changes touch code.
