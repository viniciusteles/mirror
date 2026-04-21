[< CV1.E3 Pi Session Lifecycle](../index.md)

# CV1.E3.S1 — Add `--interface pi` to conversation logger

**Status:** ✅ Done  
**Outcome:** Pi messages are logged with `interface="pi"` and Pi sessions can be started via `session-start`.

---

## Why

Without this story, Pi messages logged through `log-user` and `log-assistant`
would be created with `interface="claude_code"`, making them indistinguishable
from Claude sessions in the database and breaking per-interface analytics.

---

## What Is Built

- `log_user_message` / `log_assistant_message` — gain optional `interface` parameter (default `"claude_code"`)
- CLI `log-user` / `log-assistant` — parse `--interface <value>` flag before positional args
- `extract_pending()` — find ended conversations not yet extracted and run extraction
- `session_start()` — unmute + close_stale_orphans + backfill_pi_sessions + extract_pending
- CLI `session-start` command
- `get_unextracted_conversations()` added to `Store`
- `ConversationService._run_extraction()` extracted; marks `metadata.extracted=True`; `extract_conversation()` added

---

**See also:** [Plan](plan.md) · [Test Guide](test-guide.md) · [CV1.E3.S2](../cv1-e3-s2-backfill-orphans/index.md)
