[< CV4 Framework/User Separation](../index.md)

# CV4.E4 — Multi-User Foundation

**Epic:** More than one user home can coexist cleanly on one machine  
**Status:** Done
**Prerequisite for:** CV4.E5

---

## What This Is

CV4 is not only about moving one user's identity out of the repo. It is about
making Mirror Mind reusable as a framework.

That means one machine must be able to host more than one mirror home without
ambiguity, accidental merging, or hidden assumptions about a single default
user.

This epic defines the multi-user foundation:
- how an active user is selected
- how multiple homes coexist under `~/.mirror/`
- how config avoids ambiguity
- how later features (seeding, migration, transcript export) target one user home clearly

It does **not** require a full account-management system. This is local-first,
single-machine multi-user support through clear path selection and isolation.

Current state: active-user selection remains primarily environment-based, but
the multi-user contract is now implemented coherently. User-scoped commands now
report or honor the resolved mirror home more clearly; `list`, `seed`,
`backup`, `save`, `journal`, `week`, `tasks`, `journey`, `journeys`,
`memories`, `conversations`, `recall`, `consult`, and `conversation-logger`
all support explicit `--mirror-home` targeting for single-home operation.

---

## Done Condition

- The multi-user model is documented clearly
- Active-user selection is explicit and aligned with CV4.E1 (`MIRROR_HOME`, `MIRROR_USER`, future CLI overrides)
- No feature relies on hidden single-user assumptions
- User homes are treated as isolated units for seeding, exports, transcripts, and migration
- Follow-on implementation stories are clear enough to add multi-user-safe behavior without guesswork

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV4.E4.S1 | Define the active-user selection model and conflict rules | ✅ Done |
| CV4.E4.S2 | Define multi-user-safe behavior for user-scoped operations | ✅ Done |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

## Sequencing

S1 comes first. The selection model must be explicit before we can define how
operations behave safely across multiple user homes.

```text
S1 (selection model and conflicts)
  └── S2 (multi-user-safe operation rules)
```

---

**See also:** [CV4 Framework/User Separation](../index.md) · [CV4.E1 User Home Layout](../cv4-e1-user-home-layout/index.md) · [Decisions](../../../../project/decisions.md)
