[< CV6 Multi-User Onboarding, Identity Runtime Maturity, and Extensibility](../index.md)

# CV6.E3 — Multi-User Cleanup and Repo Boundary Audit

**Epic:** Remaining personal/framework/runtime boundary leaks are identified and cleaned up  
**Status:** Planned

---

## What This Is

CV4 moved Mirror Mind toward a multi-user framework, but some artifacts and
assumptions still blur the line between:
- core framework behavior
- user-owned identity
- repo-local development material
- personal or user-specific operational content

This epic audits and cleans those boundary leaks so new users do not inherit a
confusing or partially personal model.

---

## Done Condition

- remaining repo-personal artifacts are classified clearly
- runtime dependencies on personal or repo-local artifacts are removed where inappropriate
- docs reflect the actual ownership boundaries cleanly
- at least the highest-risk boundary leaks have an explicit resolution path

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV6.E3.S1 | Audit remaining repo/runtime/user-boundary leaks | Planned — see `cv6-e3-s1-audit-boundary-leaks/plan.md` |
| CV6.E3.S2 | Resolve or reclassify the highest-risk boundary leaks | Planned — see `cv6-e3-s2-resolve-high-risk-boundary-leaks/plan.md` |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV6](../index.md) · [CV6.E4 New User Onboarding Flow](../cv6-e4-new-user-onboarding-flow/index.md) · [CV6.E5 Extension Model for User-Specific Capabilities](../cv6-e5-extension-model/index.md)
