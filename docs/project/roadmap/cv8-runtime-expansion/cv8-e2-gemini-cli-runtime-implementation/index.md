[< CV8 Runtime Expansion](../index.md)

# CV8.E2 — Gemini CLI Runtime Implementation

**Epic:** Add a Gemini CLI runtime adapter that calls the shared Python core without duplicating Mirror Mind behavior
**Status:** Done
**Depends on:** CV8.E1 Gemini CLI Runtime Spike

---

## What This Is

CV8.E1 confirmed Gemini CLI supports L4 full parity via shell hooks. This epic
implements the adapter. The integration shape is close to Claude Code (shell
scripts reacting to lifecycle events) with one difference: Mirror Mode context
injection uses `BeforeAgent` `additionalContext` rather than a dedicated inject
hook.

Gemini CLI-specific files translate lifecycle events into `uv run python -m memory ...`
calls. They must not own Mirror Mind behavior.

---

## Done Condition

- `.gemini/hooks/` contains shell scripts for session-start, log-user, log-assistant, and session-end
- `.gemini/settings.json` registers hooks for `SessionStart`, `BeforeAgent`, `AfterAgent`, and `SessionEnd`
- session start calls `conversation-logger session-start`
- user turns are logged with `--interface gemini_cli` via `BeforeAgent`
- assistant turns are logged per turn via `AfterAgent`
- session end calls `session-end-pi <session_id>` (deferred extraction) and runs backup
- Mirror Mode injection: `BeforeAgent` hook calls `mirror load --context-only` when mirror state is active; returns identity block as `additionalContext`
- `.agents/skills/mm-*/SKILL.md` covers the minimum command surface for Gemini CLI and Codex; `.gemini/skills/` is intentionally absent to avoid duplicate/conflicting skills
- `gemini_cli` interface label is recognized in CLI reporting and conversation listing
- implementation has tests for every Python-side contract change
- no direct SQLite access from Gemini CLI files
- no hidden production DB access in tests or smoke scripts

---

## Stories

| Code | Story | Status |
|------|-------|--------|
| CV8.E2.S1 | Add `gemini_cli` interface support in Python CLI and reporting surfaces | Done (no-op — free-text field) |
| CV8.E2.S2 | Implement session lifecycle hooks (session-start, session-end) | Done |
| CV8.E2.S3 | Implement per-turn logging hooks (BeforeAgent, AfterAgent) | Done |
| CV8.E2.S4 | Implement Mirror Mode context injection via BeforeAgent | Done |
| CV8.E2.S5 | Add Gemini CLI command surface | Done via shared `.agents/skills/mm-*/SKILL.md` symlinks |
| CV8.E2.S6 | Add Builder Mode skill | Done (mm-build symlinked) |

---

## Implementation Shape

### File structure

```
.gemini/
  settings.json              — hook registration
  hooks/
    session-start.sh         — SessionStart: conversation-logger session-start
    log-user.sh              — BeforeAgent: log-user + optional mirror inject
    log-assistant.sh         — AfterAgent: log-assistant
    session-end.sh           — SessionEnd: session-end-pi + backup (best-effort)
.agents/
  skills/
    mm-mirror -> ../../.pi/skills/mm-mirror
    mm-build -> ../../.pi/skills/mm-build
    ... shared Gemini CLI/Codex skill surface
```

### Hook: SessionStart

```bash
#!/usr/bin/env bash
set -euo pipefail
uv run python -m memory conversation-logger session-start >&2
echo '{}'
```

Output: empty JSON object (no `additionalContext` needed at startup — identity
injection happens per-turn via `BeforeAgent`).

### Hook: BeforeAgent (log-user + optional mirror inject)

Reads `prompt` from stdin. Logs the user message. If mirror state is active,
also calls `mirror load --context-only` and returns the identity block as
`additionalContext`.

```bash
#!/usr/bin/env bash
set -euo pipefail
PROMPT=$(cat /dev/stdin | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('prompt',''))")

# Skip skill invocations
if [[ "$PROMPT" == /* ]]; then
  echo '{}'
  exit 0
fi

# Log user turn
uv run python -m memory conversation-logger log-user \
  "$GEMINI_SESSION_ID" "$PROMPT" --interface gemini_cli >&2

# Mirror Mode injection (conditional)
CONTEXT=$(uv run python -m memory mirror load --context-only \
  --query "$PROMPT" --session-id "$GEMINI_SESSION_ID" 2>/dev/null || echo "")

if [ -n "$CONTEXT" ]; then
  python3 -c "import json,sys; print(json.dumps({'hookSpecificOutput': {'additionalContext': sys.argv[1]}}))" "$CONTEXT"
else
  echo '{}'
fi
```

### Hook: AfterAgent (log-assistant)

```bash
#!/usr/bin/env bash
set -euo pipefail
RESPONSE=$(cat /dev/stdin | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('prompt_response',''))")
uv run python -m memory conversation-logger log-assistant \
  "$GEMINI_SESSION_ID" "$RESPONSE" --interface gemini_cli >&2
echo '{}'
```

### Hook: SessionEnd

```bash
#!/usr/bin/env bash
# Best-effort — CLI does not wait for this hook
uv run python -m memory conversation-logger session-end-pi "$GEMINI_SESSION_ID" >&2
uv run python -m memory backup --silent >&2
echo '{}'
```

### settings.json

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "name": "mirror-session-start",
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/session-start.sh",
            "timeout": 30000
          }
        ]
      }
    ],
    "BeforeAgent": [
      {
        "hooks": [
          {
            "name": "mirror-log-user",
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/log-user.sh",
            "timeout": 30000
          }
        ]
      }
    ],
    "AfterAgent": [
      {
        "hooks": [
          {
            "name": "mirror-log-assistant",
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/log-assistant.sh",
            "timeout": 30000
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "name": "mirror-session-end",
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/session-end.sh",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

---

## Skill Reuse

Gemini CLI skills share the same SKILL.md format as Pi and Codex. The project
uses `.agents/skills/mm-*` symlinks pointing to `.pi/skills/mm-*` as the single
Gemini CLI/Codex skill surface.

Do not create a parallel `.gemini/skills/` tree. Gemini CLI can discover skills
from `.agents/skills/`; keeping both `.gemini/skills/` and `.agents/skills/`
creates duplicate/conflicting command definitions.

---

## Design Constraints

- No Gemini-specific business logic
- No direct SQLite access from `.gemini/hooks/` scripts
- No runtime-specific copy of skill algorithms
- All Python commands inside the repo use `uv run`
- Hook scripts must print only valid JSON to stdout; all logging goes to stderr

---

## See also

- [CV8.E1 Gemini CLI Runtime Spike](../cv8-e1-gemini-cli-runtime-spike/index.md)
- [CV8.E3 Gemini CLI Operational Validation](../cv8-e3-gemini-cli-operational-validation/index.md)
- [Runtime Interface Contract](../../../../product/specs/runtime-interface/index.md)
- [Claude Code reference implementation](../../../../product/specs/runtime-interface/index.md#claude-code)
