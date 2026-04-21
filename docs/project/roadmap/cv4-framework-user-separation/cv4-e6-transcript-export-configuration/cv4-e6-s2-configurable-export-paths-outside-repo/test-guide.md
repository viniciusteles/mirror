[< CV4.E6.S2 Plan](plan.md)

# CV4.E6.S2 — Test Guide: Configurable transcript export paths outside the repo

## Verification Checklist

1. Transcript export defaults under `~/.mirror/<user>/exports/transcripts/`
2. `--mirror-home` targets one explicit user-home export path
3. `output_dir` overrides mirror-home/default behavior
4. `TRANSCRIPT_EXPORT_DIR` is honored when no explicit mirror home is provided
5. transcript export stays outside repository-owned source paths by default

## Automated Checks

```bash
pytest tests/unit/memory/cli/test_transcript_export.py \
       tests/unit/memory/cli/test_save.py \
       tests/unit/memory/test_config.py
```

Then run the full project verification:

```bash
pytest
ruff check src/ tests/
ruff format --check src/ tests/
pyright src/memory
git diff --check
```

## Smoke Check

Use isolated `HOME` with a user home under `~/.mirror/<user>/` and confirm:
- `python -m memory save --mirror-home ...` writes under the explicit user's
  export tree
- configured transcript export overrides redirect output outside the default
  export root when desired
