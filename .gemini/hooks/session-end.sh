#!/usr/bin/env bash
# Mirror Mind — Gemini CLI SessionEnd hook
#
# Fires when the CLI exits or the session is cleared.
# Closes the conversation record (deferred extraction, like Pi) and runs backup.
#
# ⚠️  BEST-EFFORT: Gemini CLI exits without waiting for this hook to complete.
# All work here must be fast and resilient to termination. Extraction is
# deferred to the next SessionStart (same model as Pi).
#
# Gemini hook contract:
#   stdin  — JSON: { session_id, transcript_path, cwd, hook_event_name, timestamp, reason }
#   stdout — JSON (systemMessage shown to user if present; flow-control fields ignored)
#   stderr — logs only; never parsed

set -euo pipefail

cd "${GEMINI_PROJECT_DIR}" 2>/dev/null || cd "$(dirname "$0")/../.." || exit 0

uv run python -m memory conversation-logger session-end-pi "${GEMINI_SESSION_ID}" 2>/dev/null || true
uv run python -m memory backup --silent 2>/dev/null || true

echo '{}'
