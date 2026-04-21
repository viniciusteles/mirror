[< CV4.E6 Transcript Export Configuration](../index.md)

# CV4.E6.S1 — Plan: Transcript export defaults and opt-in behavior

## What and Why

Transcript export must behave like a user-owned export artifact, not like a
repo-tracked side effect.

The CV4 contract already defines the default location under the user home:

```text
~/.mirror/<user>/exports/transcripts/
```

This story locks in the runtime behavior around that contract:
- manual export stays explicit through `python -m memory save`
- automatic export is disabled by default
- when automatic export is enabled, it writes to the configured transcript
  export path outside the repo
- transcript export remains scoped to one user home at a time

Without this story, automatic export could quietly reintroduce repo-coupled or
ambient single-user behavior even after the rest of CV4 is aligned.

## Implemented Direction

- `TRANSCRIPT_EXPORT_AUTOMATIC=false` is the default
- `TRANSCRIPT_EXPORT_DIR` defaults under the resolved user home export root
- `python -m memory save --mirror-home ...` targets one explicit user home
- `conversation-logger` only exports transcripts automatically when
  `TRANSCRIPT_EXPORT_AUTOMATIC` is enabled
- automatic export remains separate from assistant-message backfill; no export,
  no transcript-side effect

## Design Notes

- Manual export remains the safest default because it is explicit and easy to
  reason about.
- Automatic export belongs in runtime hooks, but only when the user has opted in.
- The export path contract stays outside the repo even when the runtime is
  launched from a repository checkout.

## Risks Addressed

### 1. Silent automatic exports
Disabled by default to avoid surprising writes.

### 2. Repo pollution
Export path defaults remain outside the repo.

### 3. Cross-user ambiguity
Exports are scoped to one resolved or explicit mirror home.

## Verification Focus

- automatic export disabled by default
- automatic export occurs only when explicitly enabled
- transcript export paths remain user-scoped and outside the repo
