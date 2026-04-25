[< Roadmap](../index.md)

# CV0 — English Foundation ✅

**Status:** Done  
**Completed:** 2026-04-17  
**Commits:** `fb0bcf6` through `d425b52` (~40 commits, 9 sessions)

---

## What This Was

A full migration of the Mirror Mind codebase from Portuguese domain language to
English. The system was built initially with Portuguese names throughout — the
package was `memoria`, journeys were `travessias`, the database lived in
`~/.espelho/`. Those names coupled the API surface to the author's language and
made the codebase harder to read, contribute to, and extend.

CV0 removed that coupling entirely.

---

## Why It Mattered

CV1 (Pi Runtime) would have required duplicating Portuguese-named code into a
new interface. Cleaning the domain language first gave CV1 a stable, English
foundation to build on. This was not optional cleanup — it was a prerequisite.

---

## What Was Delivered

Across all layers:

| Layer | Change |
|-------|--------|
| Python package | `memoria` → `memory` |
| Database directory | `~/.espelho/` → `~/.mirror/` |
| Database filenames | `memoria*.db` → `memory*.db` |
| Service names | `TravessiaService` → `JourneyService`, etc. |
| CLI commands | Portuguese aliases removed |
| Runtime config | `.espelho` discovery removed, `mirror` direct |
| Identity layers | `travessia`/`caminho` → `journey`/`journey_path` |
| Mirror state | `travessia` key → `journey` key |
| Extraction | Portuguese LLM response normalization removed |
| Seed loading | `identity/travessias` → `identity/journeys` |
| Identity YAMLs | Translated to English |
| Docs and prompts | Updated to English domain vocabulary |

Compatibility aliases and runtime fallbacks are gone from normal paths.
Migration-only code remains in `db/migrations.py` and `cli/migration_rehearsal.py`
to allow upgrading old databases.

---

## Outcome

- **519 tests passing** after all migration tracks
- **Isolated smoke test** validated with temporary `HOME`/`MEMORY_DIR`
- **No Portuguese runtime paths** remain outside migration-only code
- **ruff, pyright, git diff --check** all clean

---

## References

- [Decisions](../../decisions.md) — "English domain language is complete and tagged"

---

**See also:** [CV1 Pi Runtime](../cv1-pi-runtime/index.md) · [Roadmap](../index.md)
