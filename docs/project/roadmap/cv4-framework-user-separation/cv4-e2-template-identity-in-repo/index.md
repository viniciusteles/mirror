[< CV4 Framework/User Separation](../index.md)

# CV4.E2 — Template Identity in Repo

**Epic:** The repo ships only generic templates under `templates/identity/`  
**Status:** Done
**Prerequisite for:** CV4.E3, CV4.E5

---

## What This Is

Today the project still carries live identity assumptions too close to the
repository. CV4 requires a clean split:
- the repository ships framework code and bootstrap templates
- real user identity lives under `~/.mirror/<user>/identity/`

This epic defines and plans the repository side of that split.

The goal is not only to move files. The goal is to define what a *template*
is, what content belongs in it, what must be removed from repo-owned identity,
and how those templates should support bootstrap of a new user home.

Current state: the repo `identity/` tree has been removed. Generic templates
now live under `templates/identity/`, while the repository's collaboration
persona used to live separately in repo-local material for `AGENTS.md`, but no repo-local persona file is part of the framework/user-home identity model.
This keeps repo-operational guidance out of both runtime user identity and
bootstrap templates.

---

## Done Condition

- Generic identity templates live under `templates/identity/`
- Repo-owned identity content is clearly template/example material, not live user identity
- Template structure matches the intended user-home identity layout closely enough to bootstrap from it
- The docs distinguish template bootstrap assets from user-owned runtime identity
- Follow-on implementation stories are clear enough to relocate/create templates safely

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV4.E2.S1 | Define the template identity structure and content rules | ✅ Done |
| CV4.E2.S2 | Plan migration from repo-owned identity assumptions to `templates/identity/` | ✅ Done |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

## Sequencing

S1 should come first. We need a clear definition of template scope before
planning how to relocate or transform existing repo-owned identity material.

```text
S1 (template structure and content rules)
  └── S2 (migration plan for repo-owned identity assumptions)
```

---

**See also:** [CV4 Framework/User Separation](../index.md) · [Briefing D3](../../../../project/briefing.md) · [Decisions](../../../../project/decisions.md)
