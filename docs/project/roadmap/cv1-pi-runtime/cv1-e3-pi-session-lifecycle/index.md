[< CV1 Pi Runtime](../index.md)

# CV1.E3 — Pi Session Lifecycle

**Epic:** Pi sessions are remembered  
**Status:** ✅ Done  
**Requires:** CV1.E1 (Shared Command Core)

---

## What This Is

Pi sessions and transcripts live under `~/.pi/agent/sessions/`, not
`~/.claude/projects/`. The current conversation logger is Claude-oriented.

This epic extends `src/memory/cli/conversation_logger.py` with Pi lifecycle
support: `session-start`, `log-user --interface pi`, `log-assistant --interface pi`,
stale orphan closing, pending extraction, and Pi JSONL backfill.

At session end, memories are extracted the same way as Claude sessions — through
the same extraction pipeline, with the same quality guard (journey + 4+ messages).

---

## Done Condition

- `python -m memory conversation-logger session-start --interface pi` works
- `python -m memory conversation-logger log-user --interface pi ...` logs messages
- `python -m memory conversation-logger log-assistant --interface pi ...` logs responses
- `python -m memory conversation-logger session-end` triggers extraction
- Stale orphan sessions from previous runs are closed without touching the active session
- Pi JSONL transcript format is parsed correctly for backfill
- Tests cover all lifecycle commands with `--interface pi`

---

## Key Risks

- **Session ID shape differs.** Claude uses a session ID string; Pi may provide a
  session file path. This difference must be explicit and tested — not papered over.
- **Transcript format differs.** Pi JSONL and Claude JSONL are similar but not
  identical. The parser must handle both shapes or fail clearly.

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV1.E3.S1 | Add `--interface pi` to conversation logger | ✅ |
| CV1.E3.S2 | Add Pi JSONL backfill and stale orphan handling | ✅ |

Stories get `plan.md` and `test-guide.md` before implementation begins.

---

**See also:** [CV1.E1 Shared Command Core](../cv1-e1-shared-command-core/index.md) · [Pi Adoption Spike](../../../../process/spikes/pi-runtime-adoption-2026-04-17.md)
