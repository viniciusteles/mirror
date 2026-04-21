[< CV4 Framework/User Separation](../index.md)

# CV4.E6 — Transcript Export Configuration

**Epic:** Transcript exports are optional, configurable, and stored outside the repo
**Status:** Done
**Prerequisite for:** follow-on implementation after CV4.E1 path rules are stable

---

## What This Is

Transcript export is part of the user-owned runtime story, but it is not part of
repository-owned framework source.

This epic defines how transcript exports should behave under the CV4 model:
- transcript exports are optional
- transcript exports are configurable
- transcript exports default outside the repo
- transcript exports belong to one user home at a time
- automatic transcript export is opt-in

This keeps transcript artifacts aligned with framework/user separation instead of
quietly reintroducing user-owned runtime files into the repository checkout.

Current state: transcript export defaults outside the repo through the
configured transcript export path, `python -m memory save --mirror-home ...`
can target one explicit user home, and automatic transcript export now respects
`TRANSCRIPT_EXPORT_AUTOMATIC` as an explicit opt-in. The transcript export
contract is now aligned with the CV4 user-home model.

---

## Done Condition

- Transcript export defaults are defined under the user-home model
- Automatic transcript export is explicitly opt-in
- Config names and path behavior are aligned with CV4.E1
- Transcript artifacts are treated as exports, not source files
- Follow-on implementation stories are clear enough to add transcript export behavior safely

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| [CV4.E6.S1](cv4-e6-s1-transcript-export-defaults-and-opt-in-behavior/plan.md) | Define transcript export defaults, path rules, and opt-in behavior | ✅ Done |
| [CV4.E6.S2](cv4-e6-s2-configurable-export-paths-outside-repo/plan.md) | Plan implementation of configurable transcript export outside the repo | ✅ Done |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

## Sequencing

S1 should come first. We need a clear contract for transcript export ownership,
defaults, and opt-in behavior before implementation work begins.

```text
S1 (defaults, path rules, opt-in behavior)
  └── S2 (implementation plan for configurable transcript export)
```

---

**See also:** [CV4 Framework/User Separation](../index.md) · [CV4.E1 User Home Layout](../cv4-e1-user-home-layout/index.md) · [Decisions](../../../../project/decisions.md)
