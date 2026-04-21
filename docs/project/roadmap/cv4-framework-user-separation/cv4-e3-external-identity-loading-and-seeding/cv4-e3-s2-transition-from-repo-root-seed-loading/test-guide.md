[< CV4.E3.S2 Plan](plan.md)

# CV4.E3.S2 — Test Guide: Transition from repo-root seed loading to user-home seed loading

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the transition plan is explicit enough to
move seeding away from repo-root assumptions without creating hidden fallback behavior.

---

## Review Checklist

Confirm the docs clearly define:

1. **Current coupling**
   - `seed.py` is currently coupled to repo-root `identity/`
   - that coupling is treated as the thing to remove

2. **Transition direction**
   - user-home identity becomes the default seed source
   - repo-root seed loading is transitional only

3. **Compatibility stance**
   - any compatibility behavior must be explicit and time-bounded
   - no silent fallback to repo identity

4. **Documentation synchronization**
   - docs must change together with runtime seed behavior

5. **Steady-state target**
   - repo-root discovery is not part of long-term runtime seeding

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e3-external-identity-loading-and-seeding/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e3-external-identity-loading-and-seeding/cv4-e3-s1-seeding-source-of-truth-contract/plan.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e3-external-identity-loading-and-seeding/cv4-e3-s2-transition-from-repo-root-seed-loading/plan.md`

Check specifically that the wording does **not** imply:
- repo-root seed loading remains the intended architecture
- compatibility fallback may happen silently
- templates are allowed to act as runtime seed input by accident

---

## Validation Commands

```bash
rg -n "seed.py|repo-root|user-home|templates/identity|bootstrap|fallback" docs/project docs/process docs/index.md src/memory/cli/seed.py
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required because no code behavior changes are in scope.
