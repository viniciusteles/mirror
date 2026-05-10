[< CV10](../index.md)

# CV10.E1 — Coherence Core

**Status:** Planned
**User-visible outcome:** Mirror can evaluate base Units of Coherence for a
project path and write a project-visible coherence index.

---

## Why

The Maestro TypeScript POC validated the smallest coherence loop: a project
without a name has a blocking gap; resolving that gap creates a name, README,
and coherence index; the next visible gap is the missing git repository.

CV10.E1 ports that idea into the Mirror Python core so coherence can use Mirror
journeys, project paths, skills, and Builder lifecycle instead of living as a
standalone CLI.

---

## Scope

Implement the generic core only:

```text
src/memory/coherence/
  models.py
  engine.py
  project.py
  render.py
  lenses/base.py or lenses/base.yml
```

The first base lens includes:

```text
project.working_name
project.git_repository
```

The core should:

- inspect a `project_path`
- evaluate base UoCs
- return a `CoherenceResult`
- render `docs/coherence/index.md`
- keep semantic ids separate from human-facing text

This epic does not integrate with Builder yet. That is CV10.E2.

---

## Non-goals

- No XP lens yet.
- No database persistence for UoCs yet.
- No full localization.
- No audience-mode behavior.
- No new user-facing `/mm-coherence` command as the primary experience.

---

## Done Condition

CV10.E1 is done when automated tests prove:

- an empty temp project produces an open blocking `project.working_name` UoC
- resolving or pre-creating a project name resolves `project.working_name`
- a project without `.git/` produces an open important `project.git_repository` UoC
- a project with `.git/` resolves `project.git_repository`
- `docs/coherence/index.md` renders the expected UoCs
- semantic ids are present independently of display ids

---

## See also

- [Plan](plan.md)
- [Test Guide](test-guide.md)
- [Coherence Runtime Specification](../../../../product/specs/coherence-runtime/index.md)
