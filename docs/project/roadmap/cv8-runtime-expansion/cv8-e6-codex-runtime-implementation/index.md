[< CV8 Runtime Expansion](../index.md)

# CV8.E6 — Codex Runtime Implementation

**Epic:** Add a Codex runtime adapter at L3 parity using a wrapper script, JSONL backfill, and native skill discovery
**Status:** Done
**Depends on:** CV8.E5 Codex Runtime Spike

---

## What This Is

Codex has no lifecycle hooks. The integration uses a different architecture from
Claude Code and Gemini CLI:

- A **wrapper script** (`scripts/codex-mirror.sh`) handles session-start,
  launches `codex`, then backfills the session transcript after Codex exits.
- A **`backfill-codex-session` CLI command** parses Codex's JSONL transcript and
  logs user/assistant turns.
- **`.agents/skills/mm-*/SKILL.md`** symlinks give the model the full Mirror Mind
  skill surface via Codex's native skill discovery.
- **`AGENTS.md`** in the project root instructs the model about Mirror Mind.

---

## Done Condition

- `uv run python -m memory conversation-logger backfill-codex-session <jsonl>` parses
  Codex JSONL and logs user/assistant turns with `--interface codex`
- `scripts/codex-mirror.sh` exists: session-start → `codex "$@"` → JSONL detection
  → backfill → session-end-pi + backup
- `.agents/skills/mm-*/SKILL.md` — 19 symlinks pointing to `.pi/skills/mm-*/`
- `AGENTS.md` in project root references Mirror Mind and the skill surface
- `codex` interface label is recognized in CLI reporting
- smoke test proves JSONL backfill writes `interface='codex'` rows to an isolated DB
- no production DB touched in tests
- README and Getting Started updated for Codex

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E6.S1 | Add `backfill-codex-session` CLI command | Done |
| CV8.E6.S2 | Write `scripts/codex-mirror.sh` wrapper | Done |
| CV8.E6.S3 | Add `.agents/skills/mm-*/SKILL.md` symlinks | Done |
| CV8.E6.S4 | Write project `AGENTS.md` with Mirror Mind instructions | Done |
| CV8.E6.S5 | Smoke test + docs | Done |

---

## Implementation Shape

### `backfill-codex-session` CLI

Parses a Codex JSONL file and logs all turns to the memory database.

```
uv run python -m memory conversation-logger backfill-codex-session <path> [--interface codex]
```

Parsing rules:
- Read `session_meta` → extract `session_id` and `cwd`
- Read `event_msg` lines where `payload.type == "user_message"` → `payload.message`
- Read `event_msg` lines where `payload.type == "agent_message"` → `payload.message`
- Log each pair via `log-user` / `log-assistant` using the extracted session_id
- Skip empty messages; truncate at 50 KB

### Wrapper script

```bash
#!/usr/bin/env bash
set -euo pipefail
# Record marker for JSONL detection
MARKER=$(mktemp)
trap 'rm -f "$MARKER"' EXIT

cd "${CODEX_PROJECT_DIR:-$PWD}"

# 1. Session start
uv run python -m memory conversation-logger session-start >/dev/null 2>&1 || true

# 2. Run Codex (blocks until user exits)
codex "$@"
EXIT_CODE=$?

# 3. Find JSONL written after our marker (for this cwd)
SESSION_JSONL=$(find ~/.codex/sessions -name "*.jsonl" -newer "$MARKER" \
  -exec grep -l "\"cwd\":\"$PWD\"" {} + 2>/dev/null | sort | tail -1 || true)

# 4. Backfill + session end
if [[ -n "$SESSION_JSONL" ]]; then
  SESSION_ID=$(basename "$SESSION_JSONL" .jsonl | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | tail -1)
  uv run python -m memory conversation-logger backfill-codex-session \
    "$SESSION_JSONL" --interface codex >/dev/null 2>&1 || true
  uv run python -m memory conversation-logger session-end-pi \
    "${SESSION_ID}" >/dev/null 2>&1 || true
fi

uv run python -m memory backup --silent >/dev/null 2>&1 || true
exit $EXIT_CODE
```

### Skill symlinks

```
.agents/skills/mm-backup   → ../.pi/skills/mm-backup/
.agents/skills/mm-build    → ../.pi/skills/mm-build/
... (19 total)
```

### `AGENTS.md`

```markdown
# Mirror Mind

This project uses Mirror Mind. When working here:

- For personal reflection, strategy, or identity questions: use `$mm-mirror`
- For project work on a specific journey: use `$mm-build <slug>`
- To see active journeys: use `$mm-journeys`
- All other `$mm-*` commands are available via skills

Mirror Mind identity and memory are loaded automatically when you invoke
the relevant skill. You do not need to load them manually.
```

---

## Design Constraints

- `backfill-codex-session` must be idempotent: re-running on the same JSONL must
  not create duplicate messages (check conversation existence before logging)
- No Codex-specific business logic in Python
- No direct SQLite access from wrapper or AGENTS.md
- All Python commands use `uv run`

---

## See also

- [CV8.E5 Codex Runtime Spike](../cv8-e5-codex-runtime-spike/index.md)
- [CV8.E7 Codex Operational Validation](../cv8-e7-codex-operational-validation/index.md)
- [Runtime Interface Contract](../../../runtime-interface.md)
