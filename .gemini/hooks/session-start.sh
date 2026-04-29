#!/usr/bin/env bash
# Mirror Mind — Gemini CLI SessionStart hook
#
# Fires on startup, session resume, and /clear.
# Unmutes logging, closes stale orphan conversations, and extracts pending
# memories from any conversations that ended without extraction.
#
# Gemini hook contract:
#   stdin  — JSON: { session_id, transcript_path, cwd, hook_event_name, timestamp, source }
#   stdout — JSON response (empty object = no special action)
#   stderr — logs only; never parsed

set -euo pipefail

cd "${GEMINI_PROJECT_DIR}" 2>/dev/null || cd "$(dirname "$0")/../.." || exit 0

uv run python -m memory conversation-logger session-start >/dev/null 2>&1 || true

echo '{}'
