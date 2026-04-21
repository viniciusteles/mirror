[< CV1.E3 Pi Session Lifecycle](../index.md)

# CV1.E3.S2 — Pi JSONL backfill and stale orphan handling

**Status:** ✅ Done  
**Outcome:** Pi sessions from `~/.pi/agent/sessions/` are imported on `session-start`; idle open conversations are closed automatically.

---

## Why

Pi sessions that ran before this integration existed would be lost without
backfill. Conversations that were never explicitly ended (process crash, etc.)
accumulate as open orphans and block extraction. Both problems are solved in
`session_start`.

---

## What Is Built

- `close_stale_orphans(threshold_minutes=30)` — ends open conversations idle longer than threshold, skipping the current active conversation
- `backfill_pi_sessions()` — scans `~/.pi/agent/sessions/**/*.jsonl`, skips already-imported and trivial (<2 message) sessions, creates `interface="pi"` conversations with timestamps preserved
- `_parse_pi_content` / `_parse_pi_timestamp` — Pi JSONL format helpers (content as str or typed blocks; timestamp as ISO or epoch_ms)
- `get_open_conversations_idle_since(threshold_dt)` added to `Store`
- `session_start()` updated to call all three operations and report counts

---

**See also:** [Plan](plan.md) · [Test Guide](test-guide.md) · [CV1.E3.S1](../cv1-e3-s1-interface-flag/index.md)
