[< S1 Plan](plan.md)

# CV3.E1.S1 — Test Guide: `journal` CLI command

## Existing tests
```bash
pytest tests/ -k "journal" -v
```
Must pass before and after.

## Smoke test
```bash
python -m memory journal "Testing the new CLI command" --journey mirror
```
Expected: prints `📓 Journal entry recorded` with title, layer, tags, ID. Exit 0.

## Unit test (add if missing)
In `tests/unit/memory/cli/test_journal.py`:
```python
def test_journal_cli_records_entry(tmp_path, monkeypatch):
    # Patch MemoryClient to avoid DB writes
    ...
    result = runner.invoke(main, ["Test entry"])
    assert "Journal entry recorded" in result.output
```

## Full suite
```bash
pytest tests/ -x -q && ruff check src/ tests/ && ruff format --check src/ tests/ && pyright src/
```
