#!/bin/bash
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
python3 -m memory conversation-logger session-end 2>/dev/null
python3 -m memory backup --silent 2>/dev/null
exit 0
