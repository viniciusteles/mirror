[< Story](index.md)

# Plan — CV10.E1 Coherence Core

## Design

Create a Mirror-native coherence package in the Python core.

```text
src/memory/coherence/
  __init__.py
  models.py
  engine.py
  project.py
  render.py
  lenses/
    __init__.py
    base.py
```

Initial model:

```python
UnitOfCoherence
  semantic_id: str
  display_id: str
  scope: str
  lens: str
  severity: Literal["blocking", "important", "optional"]
  status: Literal["open", "resolved", "deferred", "accepted"]
  expected_state: str
  observed_state: str
  gap: str | None
  evidence: list[str]
  suggested_action: str | None

CoherenceResult
  project_path: Path
  lenses: list[str]
  units: list[UnitOfCoherence]
```

Initial project inspection:

```text
ProjectState
  project_path
  name from maestro.yml or README.md title
  has_readme
  readme_title
  has_maestro_config
  has_git_repository
```

Initial base lens:

```text
project.working_name
  blocking
  resolved when maestro.yml has name or README has H1

project.git_repository
  important
  resolved when .git exists
```

Rendering:

```text
<project_path>/docs/coherence/index.md
```

## Implementation steps

1. Add tests for empty temp project.
2. Add models.
3. Add project inspection.
4. Add base lens evaluation.
5. Add renderer.
6. Add tests for resolved project name and git repository.
7. Keep all logic in `src/memory/coherence/`; no skill surface yet.

## Compatibility notes

The implementation should avoid baking future localization or audience mode into
the core. Semantic ids are mandatory. Human-facing strings can be English for
CV10.E1, but they should be isolated enough to move later.

## Risks

- Overbuilding a generic rule engine too early.
- Letting the renderer become the source of truth.
- Accidentally creating a command-first user flow before Builder integration.

## Verification

Run:

```bash
uv run pytest tests/unit/memory/coherence
```

or the equivalent test path created during implementation.
