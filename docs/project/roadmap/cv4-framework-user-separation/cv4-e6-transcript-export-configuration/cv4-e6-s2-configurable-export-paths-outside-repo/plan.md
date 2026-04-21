[< CV4.E6 Transcript Export Configuration](../index.md)

# CV4.E6.S2 — Plan: Configurable transcript export paths outside the repo

## What and Why

CV4 requires transcript artifacts to stay outside repository-owned source.
That is true both for defaults and for overrides.

This story defines the path behavior that makes transcript export flexible
without weakening the user-home model:
- the default path lives under `~/.mirror/<user>/exports/transcripts/`
- `EXPORT_DIR` may redirect the broader export root
- `TRANSCRIPT_EXPORT_DIR` may override transcript export specifically
- `--mirror-home` may target one explicit user home for a command invocation
- an explicit output dir wins over derived defaults

## Implemented Direction

Path precedence for transcript export is:
1. explicit output dir argument (when provided by the export helper)
2. explicit `mirror_home` argument for command-scoped targeting
3. configured `TRANSCRIPT_EXPORT_DIR`
4. inherited `<EXPORT_DIR>/transcripts`
5. default `~/.mirror/<user>/exports/transcripts/`

This keeps transcript export configurable while preserving the CV4 principle
that exports are artifacts owned by a user home, not by the repository.

## Design Notes

- `save --mirror-home ...` is the main command-level user-scoping surface
- helper-level `output_dir` remains the strongest override because it is the
  most explicit destination choice
- transcript exports remain optional artifacts, not runtime truth

## Risks Addressed

### 1. Reintroducing repo writes
Defaults remain outside the repo.

### 2. Ambiguous override precedence
Explicit destination beats derived defaults.

### 3. Broken inheritance from export root
Transcript export inherits from `EXPORT_DIR` unless explicitly overridden.

## Verification Focus

- mirror-home-derived transcript export path works
- explicit output dir overrides mirror-home/default behavior
- configured transcript export dir is honored when no explicit mirror home is provided
