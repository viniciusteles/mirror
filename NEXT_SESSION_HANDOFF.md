# Next Session Handoff

Start with:
- `CLAUDE.md`
- `docs/process/worklog.md`
- `docs/project/roadmap/index.md`
- `docs/project/roadmap/cv6-intelligence-runtime-maturity/index.md`
- `docs/project/roadmap/cv7-intelligence-depth/index.md`

## Current Focus

**CV0–CV5 are complete and audited. CV6 (Multi-User Onboarding, Identity Runtime Maturity, and Extensibility) is next. The former CV6 Intelligence Depth track has moved to CV7.**

Current state:
- **CV0 English Foundation** — ✅ Done
- **CV1 Pi Runtime** — ✅ Done
- **CV2 Runtime Portability** — ✅ Done
- **CV3 Pi Skill Parity** — ✅ Done
- **CV4 Framework/User Separation** — ✅ Done
- **CV5 Multisession Safety** — ✅ Done
- **CV6 Multi-User Onboarding, Identity Runtime Maturity, and Extensibility** — Planned, broad definition agreed; detailed slices not yet written
- **CV7 Intelligence Depth** — Planned, moved from the old CV6 slot

## What was completed in this session (2026-04-20, afternoon)

**pip → uv migration.**
Full migration with lock file. `uv.lock` committed. CI uses `astral-sh/setup-uv`
+ `uv sync --frozen`. New users get a reproducible environment on first clone.
The decision driver: Mirror Mind is being opened to other users, and the lock
file is part of the trust contract.

**Thread-safety race fixed in `_bootstrap_lock`.**
`fcntl.flock` does not serialize threads within the same process — only across
processes. At 32 concurrent workers on Python 3.14, this reliably caused
`sqlite3.OperationalError: unable to open database file` during SQLite bootstrap.
Fixed by adding a per-db-path `threading.Lock` as an inner layer. Both layers
are now in place: thread lock for intra-process, flock for inter-process.

**`mm:save` and transcript export removed.**
`mm:save` was dead weight — automatic export made manual save redundant.
`TRANSCRIPT_EXPORT_AUTOMATIC` also removed. `backfill_assistant_messages`
preserved (still needed at session end).

## Process lessons from this session

**`uv run` is the boundary.** After migrating to uv, `python -m pytest` uses
the system Python (3.14 in this case) and produces different results than
`uv run pytest`. The correct command going forward for everything:
`uv run pytest tests/unit/ tests/integration/ -m "not live"`.

**flock ≠ threading.** A common mistake. `fcntl.flock` is for process-level
mutual exclusion. Threads within the same process share the file descriptor and
bypass the lock entirely. When you need both, you need both layers explicitly.

**Design for both runtimes before shipping.** The session log feature built
earlier in the day was removed in the same day because it assumed the AI would
actively edit a Markdown file during the session — which Claude Code supports
but Pi does not. The lesson: before implementing any AI-driven workflow feature,
validate that it works identically in both Claude Code and Pi. If it can't work
in Pi, reconsider whether it should exist at all.

**Lock files are a user trust contract, not just an engineering convenience.**
The reason to adopt uv with `--frozen` was not speed or tooling preference —
it was the shift in audience. When other people clone your repo, reproducibility
is the first thing they'll hit if it's missing.

## Open questions

- CV6 now needs detailed planning from the new definition. First epic should be
  persona metadata/routing, with `routing_keywords` sourced from the database,
  not from seed YAML files at runtime.
- CV6.E3 and CV6.E5 now have first concrete follow-on stories planned:
  boundary-leak resolution plus a `review-copy` reference-extension path.
- The current recommended direction is: keep `review-copy` in-repo temporarily,
  but reclassify it as a reference extension rather than core.
- Should `uv run` be documented more prominently in CLAUDE.md for future
  engineering sessions? Currently only in `docs/getting-started.md`.
