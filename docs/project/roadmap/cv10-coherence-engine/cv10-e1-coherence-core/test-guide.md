[< Story](index.md)

# Test Guide — CV10.E1 Coherence Core

This guide describes the expected verification once the story is implemented.

## Automated tests

Run the coherence unit tests:

```bash
uv run pytest tests/unit/memory/coherence
```

Expected:

```text
all coherence tests pass
```

## Manual smoke check

Create a temporary project:

```bash
tmp=$(mktemp -d)
```

Run the coherence core through the test helper or temporary CLI entry point
created during implementation. The exact command may change, but it should
evaluate the temp project and write:

```text
$tmp/docs/coherence/index.md
```

Expected initial UoCs:

```text
project.working_name  open      blocking
project.git_repository open     important
```

Create a README title:

```bash
printf '# Smoke Project\n' > "$tmp/README.md"
```

Run coherence again.

Expected:

```text
project.working_name  resolved
project.git_repository open
```

Initialize git:

```bash
git -C "$tmp" init
```

Run coherence again.

Expected:

```text
project.working_name  resolved
project.git_repository resolved
```

Inspect the generated index:

```bash
cat "$tmp/docs/coherence/index.md"
```

Expected:

```text
UoC display ids are present
semantic ids are present
resolved and open sections reflect current state
```
