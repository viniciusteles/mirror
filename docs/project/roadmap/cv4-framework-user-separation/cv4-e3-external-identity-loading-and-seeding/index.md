[< CV4 Framework/User Separation](../index.md)

# CV4.E3 — External Identity Loading and Seeding

**Epic:** Seed/load reads from the user home instead of repo-owned identity files  
**Status:** Done
**Prerequisite for:** CV4.E5

---

## What This Is

CV4.E1 defines the user-home contract. CV4.E2 defines what the repository keeps
as generic templates. This epic defines the runtime shift between them:

- seeding should read from `~/.mirror/<user>/identity/`
- runtime identity loading should no longer depend on repo-owned `identity/`
- repository templates under `templates/identity/` become bootstrap assets, not runtime inputs

Today `src/memory/cli/seed.py` still resolves the repository root and reads from
`identity/self/...`, `identity/personas/...`, and `identity/journeys/...`. That
is exactly the assumption CV4 must replace.

This epic plans the change so the code moves toward the user-home model without
blurring bootstrap templates and real identity.

---

## Done Condition

- Seeding reads from the active user home under `~/.mirror/<user>/identity/`
- Runtime identity behavior no longer depends on repo-owned live identity files
- Repository templates are used only for bootstrap/copy flows
- Path resolution for seed/load aligns with CV4.E1 (`MIRROR_HOME`, `MIRROR_USER`, explicit overrides later)
- Transitional compatibility behavior is documented clearly while implementation is in progress

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV4.E3.S1 | Define the seeding source-of-truth contract for user-home identity | ✅ Done |
| CV4.E3.S2 | Plan the transition from repo-root seed loading to user-home seed loading | ✅ Done |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

## Sequencing

S1 should come first. We need the contract for where seed/load reads from before
we plan the implementation transition.

```text
S1 (seed source-of-truth contract)
  └── S2 (transition plan for seed loading)
```

---

**See also:** [CV4 Framework/User Separation](../index.md) · [CV4.E1 User Home Layout](../cv4-e1-user-home-layout/index.md) · [CV4.E2 Template Identity in Repo](../cv4-e2-template-identity-in-repo/index.md)
