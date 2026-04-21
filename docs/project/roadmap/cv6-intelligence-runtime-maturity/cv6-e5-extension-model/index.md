[< CV6 Multi-User Onboarding, Identity Runtime Maturity, and Extensibility](../index.md)

# CV6.E5 — Extension Model for User-Specific Capabilities

**Epic:** Users can add specialized capabilities without baking them into Mirror Mind core  
**Status:** ✅ Done

---

## What This Is

Mirror Mind has accumulated several examples of valuable but user-specific
capabilities: financial tooling, X digest generation, specialized copy-review
workflows, and similar domain-specific additions. These capabilities matter to
their users, but they should not automatically become part of the framework core.

This epic defines the extension model: what belongs in core, what belongs in
user-owned identity, and what belongs in external or user-installed
capabilities.

The preferred direction is explicit integration through stable boundaries such
as CLI commands, files, APIs, attachments, or custom skills orchestrating
external tools, rather than arbitrary in-process plugin loading.

---

## Done Condition

- the boundary between core features and user-specific extensions is explicit
- supported extension integration styles are documented
- at least one existing user-specific capability has a clear migration/reference path
- docs explain how a new user can add a specialized capability without modifying framework core unnecessarily
- runtimes consume an explicit installed/runtime surface rather than source manifests directly

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV6.E5.S1 | Define the extension boundary and capability model | ✅ Done — see `cv6-e5-s1-extension-boundary-and-capability-model/plan.md` |
| CV6.E5.S2 | Establish the first extension migration/reference path | ✅ Done — see `cv6-e5-s2-review-copy-reference-path/plan.md` |
| CV6.E5.S3 | Define the external skill registry and manifest contract | ✅ Done — see `cv6-e5-s3-external-skill-registry-and-manifest-contract/plan.md` |
| CV6.E5.S3A | Define the `skill.yaml` v1 contract | ✅ Done — see `cv6-e5-s3a-skill-yaml-v1-contract/plan.md` |
| CV6.E5.S4 | Migrate `review-copy` to the external skill model | ✅ Done — see `cv6-e5-s4-migrate-review-copy-to-external-skill-model/plan.md` |

Completed in practice through manifest validation, extension discovery,
inspection, sync/install/uninstall commands, runtime catalogs, Pi runtime
consumption, Claude project exposure/cleanup, and the full migration of
`review-copy` to the external skill model.

---

**See also:** [CV6](../index.md)
