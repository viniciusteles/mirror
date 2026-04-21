[< CV6 Multi-User Onboarding, Identity Runtime Maturity, and Extensibility](../index.md)

# CV6.E4 — New User Onboarding Flow

**Epic:** A new user can bootstrap, customize, seed, verify, and start using Mirror Mind without touching personal repo-owned artifacts  
**Status:** Planned

---

## What This Is

A framework is not truly multi-user just because the architecture supports more
than one user home. A new user needs a real onboarding path: bootstrap generic
identity templates, customize user-owned identity, seed the database, verify the
result, and start using the system with confidence.

This epic turns that path into a documented and testable workflow.

---

## Done Condition

- onboarding for a new user is documented from install through first successful use
- bootstrap, identity editing, seeding, and verification are clearly distinguished
- docs and tooling do not imply repo-owned personal artifacts are part of the onboarding path
- a new user can verify seeded personas, journeys, and identity metadata from the database

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV6.E4.S1 | Define the end-to-end onboarding contract for a new user | Planned |
| CV6.E4.S2 | Close the highest-friction gaps in the onboarding flow | Planned |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV6](../index.md) · [CV6.E3 Multi-User Cleanup and Repo Boundary Audit](../cv6-e3-multi-user-cleanup-and-boundary-audit/index.md)
