[< CV2.E2 Hook Dispatch to CLI](../index.md)

# CV2.E2.S1 — Plan: Expose mirror load as CLI command

## Status: Already Done

`python -m memory mirror load` already accepts all required flags:
`--context-only`, `--query`, `--persona`, `--journey`, `--org`.

Verified:
```bash
python3 -m memory mirror load --help
# usage: python3 -m memory load [-h] [--persona] [--journey] [--query] [--org] [--context-only]

python3 -m memory mirror load --context-only --query "test"
# ⏺ Mirror Mode active
# === self/soul ===  ...
```

No implementation required. S2 can proceed directly.
