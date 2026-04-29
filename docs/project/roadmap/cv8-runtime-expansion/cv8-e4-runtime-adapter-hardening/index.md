[< CV8 Runtime Expansion](../index.md)

# CV8.E4 — Runtime Adapter Hardening

**Epic:** Fold Gemini CLI lessons into the shared runtime contract before starting Codex
**Status:** In progress
**Depends on:** CV8.E3 Gemini CLI Operational Validation & Docs

---

## What This Is

Gemini CLI is the first new runtime after Pi. It exposed real assumptions in the
runtime contract: stdout purity for shell-hook runtimes, session ID delivery
models, the two extraction patterns (immediate vs deferred), the two injection
models (automatic per-turn vs explicit), DB isolation technique for smoke tests,
and the skill-symlink sharing pattern.

This epic prevents Codex from repeating the same discovery work. We harvest
what Gemini CLI taught us and turn it into explicit contract language, a
reusable smoke-test pattern, and a Codex pre-work checklist. The goal is not
abstraction for its own sake — it is making the known knowns explicit so the
Codex spike can focus on the remaining unknowns.

---

## Lessons from Gemini CLI

### L1 — Stdout purity is a hard constraint for shell-hook runtimes

Gemini CLI's hook contract: **stdout must contain only the final JSON object.**
Even a single non-JSON line breaks parsing. Found live: `session-start.sh` was
printing `"Conversation logging ACTIVE."` to stdout before the JSON object.
Fixed by redirecting Python command output to `/dev/null`. Claude Code has the
same constraint but does not use a JSON envelope — it was less visible there.

**Contract addition:** all shell-hook runtimes must redirect non-JSON CLI
output to stderr or `/dev/null`. Hooks must print exactly one JSON object to
stdout (or nothing, which the runtime treats as success).

### L2 — Session ID delivery varies by runtime model

| Runtime | Session ID source |
|---|---|
| Claude Code | JSON stdin: `session_id` field |
| Gemini CLI | JSON stdin: `session_id` field **and** `$GEMINI_SESSION_ID` env var |
| Pi | TypeScript `session.id` from extension context |

**Contract addition:** shell-hook runtimes should prefer the env var form when
available (no subprocess required to extract). Document the expected env var
name per runtime.

### L3 — Two extraction models, both proven

| Model | When | Runtimes |
|---|---|---|
| Immediate | Session end can supply `transcript_path` | Claude Code |
| Deferred | Session end is best-effort or no transcript | Pi, Gemini CLI |

**Contract addition:** make the two models explicit and state the tradeoff
(immediate extraction = better memory freshness; deferred = resilient to
best-effort session-end hooks).

### L4 — Two injection models, different UX implications

| Model | How | Runtimes |
|---|---|---|
| Automatic per-turn | `BeforeAgent` `additionalContext` | Gemini CLI |
| Explicit invocation | User types `/mm-mirror` | Pi |
| Hook-conditional | `UserPromptSubmit` inject when active | Claude Code |

**Contract addition:** document the three injection models and their tradeoffs.
Automatic per-turn (Gemini CLI model) gives the best UX at the cost of latency
on every turn. Explicit invocation (Pi model) is zero-cost when not needed.

### L5 — DB_PATH is the correct smoke-test isolation primitive

`MIRROR_HOME` conflicts with `MIRROR_USER` from `.env` when the path basename
doesn't match the user. `DB_PATH` overrides the database path directly without
touching home resolution. All future smoke tests should use `DB_PATH`.

**Contract addition:** document the isolation pattern: `DB_PATH=/tmp/smoke/memory.db`.

### L6 — Skill symlinks enable zero-maintenance skill sharing

`.gemini/skills/mm-*/` → `.pi/skills/mm-*/` via symlinks. Pi-format SKILL.md
works identically in both runtimes. New runtimes that support native SKILL.md
discovery can participate in this pattern immediately.

**Contract addition:** document the symlink pattern for runtimes that support
SKILL.md natively.

### L7 — No Python changes needed to add a new interface label

`interface` is a free-text field. Passing `--interface gemini_cli` was all that
was needed. New runtimes never require Python migrations just to add a label.

---

## Done Condition

- ✅ E4 index rewritten: Gemini CLI lessons, not Codex
- ✅ `docs/project/runtime-interface.md` updated with lessons L1–L7 as explicit
  contract sections
- ✅ Smoke test isolation pattern documented in the runtime contract
- ✅ Codex implementation checklist produced from Gemini lessons (pre-work for E5)
- ✅ No unnecessary abstraction introduced

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E4.S1 | Rewrite E4 index with Gemini CLI lessons | Done |
| CV8.E4.S2 | Update Runtime Interface Contract with L1–L7 refinements | Done |
| CV8.E4.S3 | Document smoke test isolation pattern | Done |
| CV8.E4.S4 | Produce Codex implementation checklist for E5 | Done |

---

## Guardrail

Do not build a generic runtime framework in the abstract. Extract only what
Gemini CLI made concrete and Codex is about to reuse.

> Two runtimes justify a pattern. One runtime justifies a note.

---

## See also

- [CV8.E3 Gemini CLI Operational Validation](../cv8-e3-gemini-cli-operational-validation/index.md)
- [CV8.E5 Codex Runtime Spike](../cv8-e5-codex-runtime-spike/index.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
