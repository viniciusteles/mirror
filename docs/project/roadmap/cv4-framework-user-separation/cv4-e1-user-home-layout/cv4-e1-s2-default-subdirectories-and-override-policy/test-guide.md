[< CV4.E1.S2 Plan](plan.md)

# CV4.E1.S2 — Test Guide: Define default subdirectories and override policy

## Scope

This story is planning/documentation only. No runtime implementation is in scope.

Verification is about confirming that the default layout and override-policy
rules are precise enough for later implementation.

---

## Review Checklist

Confirm the docs clearly distinguish:

1. **Fixed contract paths**
   - `identity/`
   - `memory.db`

2. **Default but overridable paths**
   - `backups/`
   - `exports/`
   - `exports/transcripts/`

3. **Primary contract source**
   - defaults derive from `MIRROR_HOME`
   - `DB_PATH` is treated as compatibility-only, not primary

4. **Override policy**
   - overrides exist only where there is strong user value
   - export and backup paths may live outside the user home
   - transcript export remains explicit and understandable
   - transcript export inherits from `EXPORT_DIR` unless `TRANSCRIPT_EXPORT_DIR` is explicitly set

5. **Compatibility awareness**
   - old path variables may remain temporarily for migration/compatibility
   - they should not obscure `MIRROR_HOME` as the primary contract

---

## Manual Verification

Read these docs together and confirm they agree:

- `docs/project/briefing.md`
- `docs/project/decisions.md`
- `docs/project/roadmap/cv4-framework-user-separation/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e1-user-home-layout/index.md`
- `docs/project/roadmap/cv4-framework-user-separation/cv4-e1-user-home-layout/cv4-e1-s2-default-subdirectories-and-override-policy/plan.md`

Check specifically that the text does **not** imply:
- backups/exports are runtime truth
- every path requires configuration
- transcript export must stay inside the repo

---

## Validation Commands

```bash
rg -n "MIRROR_HOME|TRANSCRIPT_EXPORT_DIR|backups/|exports/|memory.db|identity/" docs/project docs/process docs/index.md
```

Then run:

```bash
git diff --check
```

No runtime verification suite is required for this story because no code behavior
changes are in scope.
