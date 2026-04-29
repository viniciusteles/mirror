#!/usr/bin/env bash
set -euo pipefail

# Record marker for JSONL detection
MARKER=$(mktemp)
trap 'rm -f "$MARKER"' EXIT

cd "${CODEX_PROJECT_DIR:-$PWD}"

# 1. Session start
# We redirect to /dev/null to keep the output clean for Codex if needed,
# though here it's just a wrapper.
uv run python -m memory conversation-logger session-start >/dev/null 2>&1 || true

# 2. Run Codex (blocks until user exits)
# Use 'command codex' to avoid calling this script recursively if it's named 'codex'
# in some PATHs, though here we named it codex-mirror.sh.
codex "$@"
EXIT_CODE=$?

# 3. Find JSONL written after our marker (for this cwd)
# Codex writes sessions to ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
# We search for files newer than our MARKER that contain our current PWD in session_meta.
SESSION_JSONL=$(find ~/.codex/sessions -name "*.jsonl" -newer "$MARKER" \
  -exec grep -l "\"cwd\":\"$PWD\"" {} + 2>/dev/null | sort | tail -1 || true)

# 4. Backfill + session end
if [[ -n "$SESSION_JSONL" ]]; then
  # Extract session ID from filename: rollout-YYYY-MM-DDTHH-mm-ss-<uuid>.jsonl
  SESSION_ID=$(basename "$SESSION_JSONL" .jsonl | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | tail -1)
  
  if [[ -n "$SESSION_ID" ]]; then
    uv run python -m memory conversation-logger backfill-codex-session \
      "$SESSION_JSONL" --interface codex >/dev/null 2>&1 || true
      
    uv run python -m memory conversation-logger session-end-pi \
      "${SESSION_ID}" >/dev/null 2>&1 || true
  fi
fi

# 5. Backup (silent)
uv run python -m memory backup --silent >/dev/null 2>&1 || true

exit $EXIT_CODE
