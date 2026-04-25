[< CV6 Multi-User Onboarding, Identity Runtime Maturity, and Extensibility](../index.md)

# CV6.E4 — New User Onboarding Flow

**Epic:** A new user can bootstrap, customize, seed, verify, and start using Mirror Mind without touching personal repo-owned artifacts  
**Status:** ✅ Done

---

## What This Is

A framework is not truly multi-user just because the architecture supports more
than one user home. A new user needs a real onboarding path: bootstrap generic
identity templates, customize user-owned identity, seed the database, verify the
result, and start using the system with confidence.

This epic turns that path into a documented and testable workflow.

Completed outcome:
- `docs/getting-started.md` covers install, bootstrap, identity editing,
  seeding, verification, and the extension flow
- onboarding docs point users at `~/.mirror/<user>/identity/` and the
  database/runtime model instead of repo-local personal artifacts
- starter templates now seed meaningful defaults instead of placeholder records:
  `writer`, `thinker`, `engineer`, and `personal-growth`
- verification commands exercise database-backed persona metadata, routing, and
  journey listing from a fresh user home

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
| CV6.E4.S1 | Define the end-to-end onboarding contract for a new user | ✅ Done |
| CV6.E4.S2 | Close the highest-friction gaps in the onboarding flow | ✅ Done |

This epic is complete: a new user can bootstrap a user home, review meaningful
starter identity assets, seed the database, verify personas/journeys/routing,
and start using Mirror Mind without touching repo-owned personal artifacts.

---

**See also:** [CV6](../index.md) · [CV6.E3 Multi-User Cleanup and Repo Boundary Audit](../cv6-e3-multi-user-cleanup-and-boundary-audit/index.md)
