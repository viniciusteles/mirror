---
name: "mm-mute"
description: Toggles conversation logging on or off
user-invocable: true
---

# Mute

When receiving `/mm-mute`:

1. Check current status:
   ```bash
   python -m memory conversation-logger status
   ```

2. Toggle:
   - If **ACTIVE**: run `python -m memory conversation-logger mute` → say "Conversation logging muted."
   - If **MUTED**: run `python -m memory conversation-logger unmute` → say "Conversation logging reactivated."
