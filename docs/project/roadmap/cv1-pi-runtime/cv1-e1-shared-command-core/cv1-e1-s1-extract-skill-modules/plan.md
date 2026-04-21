[< S1 Index](index.md)

# Plan — CV1.E1.S1

## Goal

Move Mirror Mode logic from `.claude/skills/mm:mirror/run.py` into an importable Python module so both Claude and Pi can call the same implementation.

---

## Deliverables

### 1. `src/memory/skills/__init__.py`
Empty package marker.

### 2. `src/memory/hooks/mirror_state.py` — gains `write_state()`

```python
def write_state(
    active: bool,
    persona: str | None = None,
    journey: str | None = None,
    path: Path = DEFAULT_STATE_PATH,
) -> None:
    """Write Mirror Mode active/inactive state to disk."""
```

The existing `_write_mirror_state` in `run.py` is removed. `mirror_state.py` becomes the single owner of both state reads and writes.

### 3. `src/memory/skills/mirror.py`

Five public functions. No stderr/stdout output — callers handle display.

```python
def load(
    journey: str | None = None,
    persona: str | None = None,
    query: str | None = None,
    org: bool = False,
    context_only: bool = False,
    env: str | None = None,
) -> tuple[str, str | None, list | None]:
    """Activate Mirror Mode.
    Returns (context_str, resolved_journey, detected_matches_or_None).
    Side effects: writes mirror state, switches conversation (unless context_only).
    """

def deactivate() -> None:
    """Clear mirror state file."""

def log(summary: str) -> None:
    """Record assistant response to current session. No-op if muted."""

def list_journeys(env: str | None = None) -> list[dict]:
    """Return active journeys as list of dicts."""

def title_from_summary(summary: str) -> str:
    """Extract a ≤60-char title from the first sentence of a summary."""
```

### 4. `.claude/skills/mm:mirror/run.py` — thin wrapper

```python
from memory.skills.mirror import load, deactivate, log, list_journeys

def cmd_load(args):
    context, resolved_journey, detected = load(
        journey=args.journey,
        persona=args.persona,
        query=args.query,
        org=args.org,
        context_only=args.context_only,
    )
    if detected:
        _print_detection_info(detected[0])  # stderr
    _print_mirror_banner(args.persona)       # stderr
    print(context)                           # stdout → Claude injects this

def cmd_deactivate(args): deactivate()
def cmd_log(args): log(args.resumo)
def cmd_journeys(args):
    for j in list_journeys():
        print(f"- **{j['id']}** — {j['name']}: {j['description']}")
```

`PERSONA_ICONS`, `_print_mirror_banner`, `_print_detection_info` stay in `run.py` — they are interface-specific display logic.

### 5. `tests/unit/memory/skills/test_mirror.py`

| Test | What it verifies |
|------|-----------------|
| `test_load_returns_context_and_journey` | Calls `load_mirror_context`, returns (context, journey, None) |
| `test_load_detects_journey_from_query` | Calls `detect_journey` when journey=None and query given |
| `test_load_skips_switch_when_context_only` | `switch_conversation` not called when `context_only=True` |
| `test_load_calls_switch_conversation` | `switch_conversation` called with correct args when not context_only |
| `test_deactivate_writes_inactive_state` | `write_state(active=False)` called |
| `test_log_records_to_current_session` | `log_assistant_to_current` called with summary |
| `test_log_is_noop_when_muted` | No call to `log_assistant_to_current` when muted |
| `test_title_from_summary_short` | Short sentence returned as-is |
| `test_title_from_summary_long` | >60 chars truncated at word boundary with "..." |

---

## Implementation Order

1. Add `write_state()` to `src/memory/hooks/mirror_state.py`
2. Create `src/memory/skills/__init__.py`
3. Create `src/memory/skills/mirror.py` (all five functions)
4. Update `.claude/skills/mm:mirror/run.py` to thin wrapper (remove `_write_mirror_state`, `_read_mirror_state`)
5. Add `tests/unit/memory/skills/__init__.py` + `test_mirror.py`
6. Verify: `pytest tests/unit/memory/skills/`
