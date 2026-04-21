[< CV4.E6.S1 Plan](plan.md)

# CV4.E6.S1 — Test Guide: Transcript export defaults and opt-in behavior

## Verification Checklist

1. `TRANSCRIPT_EXPORT_AUTOMATIC` defaults to `false`
2. `TRANSCRIPT_EXPORT_DIR` defaults under the resolved user-home export path
3. `python -m memory save --mirror-home ...` exports to the explicit user's
   transcript export directory
4. `conversation-logger` does not export transcripts automatically when
   `TRANSCRIPT_EXPORT_AUTOMATIC=false`
5. `conversation-logger` does export transcripts automatically when
   `TRANSCRIPT_EXPORT_AUTOMATIC=true`

## Automated Checks

```bash
pytest tests/unit/memory/test_config.py \
       tests/unit/memory/cli/test_save.py \
       tests/unit/memory/cli/test_transcript_export.py \
       tests/unit/memory/cli/test_conversation_logger_auto_export.py
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

With isolated `HOME` and explicit `MIRROR_HOME`, confirm:
- manual `python -m memory save --mirror-home ...` writes under
  `~/.mirror/<user>/exports/transcripts/`
- automatic export only happens when `TRANSCRIPT_EXPORT_AUTOMATIC=true`
