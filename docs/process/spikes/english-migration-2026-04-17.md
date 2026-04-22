[< Process](../development-guide.md)

# Spike: English Domain Language Migration

**Date:** 2026-04-17  
**Duration:** 9 sessions, ~40 commits  
**Outcome:** CV0 English Foundation complete

---

## Motivation

The Mirror Mind codebase was built initially in Portuguese. The package was
`memoria`, journeys were `travessias`, the database lived in `~/.espelho/`,
identity layers used `caminho` and `travessia` as keys.

This coupling had real costs:
- The API surface was unreadable to anyone who doesn't read Portuguese
- Adding Pi support would have required porting Portuguese-named code into a new interface
- Contributing to or auditing the codebase required translating domain terms mentally

The migration removed that coupling. The result is a codebase that can be extended, read, and contributed to without knowing Portuguese.

---

## What Was Done

The migration proceeded in layers, from the most fundamental to the most surface:

1. **English API aliases added** alongside Portuguese names
2. **Python package renamed** from `memoria` to `memory` (with executable compatibility)
3. **Portuguese primary aliases removed** from `MemoryClient`
4. **Database artifacts renamed** from `memoria*` to `memory*`
5. **Legacy `memoria` package removed** from `src/`
6. **Database path renamed** from `~/.espelho/` to `~/.mirror/`
7. **Portuguese CLI aliases removed**
8. **Runtime legacy data compatibility removed** (config, seed, services, extraction)
9. **Identity YAMLs translated** to English content
10. **Docs and prompts updated** to English domain vocabulary

Each layer was validated before the next began. The compatibility window
(keeping Portuguese aliases while adding English ones) allowed the migration to
be incremental rather than a single risky cutover.

---

## Key Decisions

**Compatibility window before removal.**  
English aliases were added first, verified working, then Portuguese aliases were
removed. This reduced risk at each step.

**Migration-only support stays.**  
Database migrations and migration rehearsal code still handle old schemas and
Portuguese-era layer values so old databases can be upgraded. This is intentional:
removing migration-only support is a separate decision when old database upgrade
is no longer needed.

**Smoke test pattern established.**  
Isolated `HOME` + explicit `MEMORY_DIR` + empty-string env vars prevents `.env`
from repopulating paths during subprocess invocation. This pattern is reusable
for any future end-to-end validation.

**Migration plan as a living document.**  
`docs/english-domain-language-migration-plan.md` was updated throughout the
migration. It served as the source of truth for what had been done and what
remained.

---

## What We Learned

**The compatibility window is worth the extra work.**  
Removing aliases before verifying replacements would have broken things mid-migration.
Adding first, removing second, validating between — this is the right sequence.

**Isolated smoke tests catch what unit tests miss.**  
The isolated end-to-end smoke test (temporary `HOME`, real subprocesses, empty env
vars) caught path issues that unit tests with mocks would never surface. The smoke
test is now a standard part of the verification checklist for any CV.

**Session logs are worth writing.**  
The 9 session logs (001–009) in `docs/session-logs/2026/` are a complete record
of the migration. They were used to reconstruct the handoff context and will
remain available as historical reference.

**`NEXT_SESSION_HANDOFF.md` was the operational thread.**  
Without it, context would have been lost between sessions. The worklog replaces
this function going forward — but the handoff pattern (explicit state, explicit
next steps) is worth preserving.

---

## References

- `docs/english-domain-language-migration-plan.md` — full migration plan
- `docs/portuguese-domain-language-inventory.md` — original inventory
- `docs/session-logs/2026/2026-04-16-001-memory-naming-cleanup.md` through `009`
- [CV0 English Foundation](../../project/roadmap/cv0-english-foundation/index.md)
- [Decisions](../../project/decisions.md) — "English domain language is complete and tagged"

---

**See also:** [Development Guide](../development-guide.md) · [CV0 English Foundation](../../project/roadmap/cv0-english-foundation/index.md)
