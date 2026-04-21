#!/bin/bash
# Ensure conversation logging is active when a session starts.
cd "$(dirname "$0")/../.." || exit 0
python3 -m memory conversation-logger session-start 2>/dev/null || true
exit 0
