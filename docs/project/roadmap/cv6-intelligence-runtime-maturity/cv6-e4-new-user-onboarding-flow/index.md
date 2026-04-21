[< CV6 Multi-User Onboarding, Identity Runtime Maturity, and Extensibility](../index.md)

# CV6.E4 — New User Onboarding Flow

**Epic:** A new user can bootstrap, customize, seed, verify, and start using Mirror Mind without touching personal repo-owned artifacts  
**Status:** In Progress

---

## What This Is

A framework is not truly multi-user just because the architecture supports more
than one user home. A new user needs a real onboarding path: bootstrap generic
identity templates, customize user-owned identity, seed the database, verify the
result, and start using the system with confidence.

This epic turns that path into a documented and testable workflow.

Progress so far:
- `docs/getting-started.md` now covers install, bootstrap, identity editing,
  seeding, verification, and the extension flow
- onboarding docs now point users at `~/.mirror/<user>/identity/` and the
  database/runtime model instead of repo-local personal artifacts
- extension usage is documented as part of the newcomer path

Remaining work is mainly about deciding whether more explicit verification or
workflow hardening is still needed beyond the current docs.

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
| CV6.E4.S1 | Define the end-to-end onboarding contract for a new user | In Progress |
| CV6.E4.S2 | Close the highest-friction gaps in the onboarding flow | In Progress |

This epic is partially implemented through the current getting-started and
reference documentation, but remains open until the onboarding path is judged
complete and verifiable enough for new users.

---

**See also:** [CV6](../index.md) · [CV6.E3 Multi-User Cleanup and Repo Boundary Audit](../cv6-e3-multi-user-cleanup-and-boundary-audit/index.md)
