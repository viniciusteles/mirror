[< CV1.E1 Shared Command Core](../index.md)

# CV1.E1.S2 — Add unified `python -m memory` CLI commands

**Status:** ✅ Done  
**Outcome:** Both Claude and Pi can invoke mirror and conversation-logger operations via `python -m memory <command>` without calling skill script paths directly.

---

## Why

The Pi extension needs to call `python -m memory conversation-logger session-start` (and similar) without knowing the path to `.claude/skills/`. A unified CLI entry point decouples the interface layer from the filesystem layout of the repository.

---

## What Is Built

- `src/memory/__main__.py` — gains `mirror` and `conversation-logger` routing
- `src/memory/skills/mirror.py` — gains `main(argv)` for CLI dispatch
- `src/memory/cli/conversation_logger.py` — gains `main(argv)` extracted from `__name__` block
- `tests/unit/memory/test_main.py` — extended with dispatch tests

### New commands

```
python -m memory mirror load [--persona P] [--journey J] [--query Q] [--org] [--context-only]
python -m memory mirror deactivate
python -m memory mirror log "summary"
python -m memory mirror journeys

python -m memory conversation-logger user-prompt
python -m memory conversation-logger session-end
python -m memory conversation-logger mute
python -m memory conversation-logger unmute
python -m memory conversation-logger status
python -m memory conversation-logger switch
python -m memory conversation-logger log-user <session_id> <content>
python -m memory conversation-logger log-assistant <session_id> <content>
```

---

**See also:** [Plan](plan.md) · [Test Guide](test-guide.md) · [CV1.E1.S1](../cv1-e1-s1-extract-skill-modules/index.md)
