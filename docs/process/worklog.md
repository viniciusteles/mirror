[< Docs](../index.md)

# Worklog

Operational progress. This file records what was delivered and what is next.
Update when a meaningful milestone is reached.

---

## Done

### 2026-04-22 — credits clarified and Pi repositioned as the preferred runtime

Updated `README.md` and `docs/getting-started.md` to make the project's lineage
explicit. The docs now clearly credit **Alisson Vale** and link to the original
`alissonvale/mirror-poc` repository as the source of the mirror concept and the
first implementation. They also credit **Henrique Bastos** and link to
`henriquebastos/mirror-mind` for the Pi direction that influenced the move
toward a more model-flexible runtime.

The user-facing positioning was also adjusted: Claude Code is now described as
the original harness and still-supported alternative, while Pi is presented as
the preferred runtime because it better supports a multi-model future. README
and getting-started instructions now introduce Pi first and Claude second.

Follow-up corrections aligned the public repository naming with
`viniciusteles/mirror` (no current-project `mirror-poc` references in docs) and
normalized Pi links to the agent package URL:
`https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent`.

---

### 2026-04-22 — onboarding and runtime command docs aligned with uv

Standardized current-facing docs and skill instructions around `uv run` as the
repo command boundary. Updated `docs/getting-started.md`, `README.md`,
`REFERENCE.md`, `CLAUDE.md`, `docs/project/runtime-interface.md`, Claude/Pi
skill docs, and local Claude settings so project Python commands and tests run
through the locked uv environment instead of system Python.

Onboarding was also tightened: `docs/getting-started.md` now uses CLI-first
seeding (`uv run python -m memory seed`), adds stronger verification commands
for personas, journeys, persona metadata, and routing, and includes a compact
success checklist for new users. Seed guidance in runtime skills was corrected
to point at user-home identity files rather than repository-owned identity
artifacts.

Committed as `c11acde` (`Standardize uv-run docs and tighten onboarding verification`).
CI green on the push.

---

### 2026-04-20 — sqlite3 connection fd leak fixed in MemoryClient

**Symptom.** After the thread-safety fix, `test_concurrent_memory_client_open_on_fresh_db_is_safe` still failed intermittently with `sqlite3.OperationalError: unable to open database file`, reliably on Vinícius's machine, never on the agent's. Same line (`sqlite3.connect`) every time. A retry-with-backoff guard made failures take 6 s instead of 0 s — the symptom was persistent, not a filesystem flicker.

**Root cause.** Python 3.14's `sqlite3.Connection` does not release its underlying OS file descriptors through refcount-based cleanup. Only explicit `close()` or process exit releases them. The concurrency test creates 32 × 5 = 160 short-lived `MemoryClient` instances with no explicit close, leaking ∼2 fds per client. On a machine where cyclic GC doesn't run often enough between iterations, the process hits `EMFILE` and SQLite reports `unable to open database file`.

**Fix.** Added explicit lifecycle management to `MemoryClient`:
- `close()` closes the SQLite connection. Idempotent.
- `__enter__` / `__exit__` so callers can use `with MemoryClient(...) as mem:`.
- `__del__` as a best-effort safety net for callers that forget to close.
The concurrency test now closes every client it opens. Verified: leaked fds drop to zero without `gc.collect()`, and the test suite runs green across 30+ consecutive invocations on both machines where the failure reproduced.

**Side fix.** `mirror_state.mark_injected` previously constructed two `MemoryClient` instances back-to-back for a single hook invocation (read + write), doubling bootstrap cost. Now reuses one client across both store calls.

**Lesson.** When a fix doesn't work, treat the new timing data as a diagnostic signal. A retry that slows failures from 0 s to 6 s tells you the error is *persistent*, not *transient* — so the hypothesis was wrong, and the retry is masking symptoms of the real cause. Step back and re-instrument rather than iterate on the wrong hypothesis.

624 tests passing. CI green on Python 3.10 and 3.12.

---

### 2026-04-20 — pip replaced with uv; thread-safety race fixed

**uv migration (full, with lock file).** Replaced `setup-python` + `pip install`
with `astral-sh/setup-uv` + `uv sync --frozen` in CI. Generated `uv.lock` and
committed it. New users now get a byte-identical environment on first clone.
README and `docs/getting-started.md` updated: uv added to prerequisites, pip
references removed, stale `mm:save` entries cleaned up.

**Thread-safety race in bootstrap lock fixed.** `fcntl.flock` is a
cross-process primitive and does not serialize threads within the same process.
Under 32 concurrent workers on Python 3.14 this caused
`sqlite3.OperationalError: unable to open database file` during bootstrap.
Fixed by adding a per-db-path `threading.Lock` as an inner layer inside
`_bootstrap_lock`. `flock` remains for cross-process safety; the thread lock
serializes concurrent threads within one process.

**`mm:save` and transcript export removed.** `mm:save` had no practical use
case with `SESSION_LOG_AUTOMATIC` enabled and was removed entirely. The automatic
JSONL→Markdown transcript export (`TRANSCRIPT_EXPORT_AUTOMATIC`) was also
removed. `backfill_assistant_messages` is preserved — it still runs at session
end to capture assistant turns in the DB.

624 tests passing. CI green on Python 3.10 and 3.12.

---

### 2026-04-20 — Session log feature and one-off migration tool removed

Two cleanups driven by real usage findings on Pi.

**Session log removed.** The feature was built assuming the AI would actively
edit a log file during the session — which Claude Code supports but Pi does not.
On Pi, every session produced an empty skeleton with a "session" placeholder topic
and no content. Removed entirely: `src/memory/cli/session_log.py`, config entries
`SESSION_LOG_AUTOMATIC` / `SESSION_LOG_DIR`, all skill step references in both
`.claude/` and `.pi/` skills, the `docs/session-logs/` tree, and associated tests.
Pi's native logging is the replacement. Historical session logs moved to Dropbox.

**`src/memory/tools/` removed.** The `identity_english_migration.py` one-off tool
served its purpose during CV0 English migration and had been dead weight since.
Deleted with its tests.

624 tests passing. CI green.

---

### 2026-04-19 — CV5 audit and follow-up fixes

Independent audit of the CV4 + CV5 implementation. Findings: the CV5.E2.S2
concurrent-startup regression test was flaky (~20% failure rate); `/mm:save`
was silently targeting the wrong transcript after CV5 removed the writers of
`CURRENT_SESSION_PATH`; `backfill_pi_sessions` ignored `mirror_home`; mirror
state CLIs silently no-op'd on missing `--session-id`; `mirror deactivate`
CLI was effectively dead; and several state-file config constants and one
helper module had become dead code.

Landed in six verified commits. Concurrency regression test now passes 50/50
under stress. `REFERENCE.md` now documents the `runtime_sessions` table and
the CV5 session model. Retroactive session log added for the original CV5
implementation plus a log for this audit session.



---

### 2026-04-19 — CV5 Multisession Safety complete

Replaced singleton runtime state with a SQLite-backed `runtime_sessions`
registry. Session ↔ conversation routing is now database-backed and covered by
concurrency regression tests; mirror mode state is session-scoped; stale-orphan
cleanup skips every active runtime session instead of one ambient session; and
Claude hook reinjection now passes explicit `session_id` through the safer
runtime path. Concurrent startup against a fresh database no longer trips
migration integrity failures.

Reference: [CV5 Multisession Safety](../project/roadmap/cv5-multisession-safety/index.md)

---

### 2026-04-17 — CV0 English Foundation complete

Full Portuguese→English migration across all layers: Python API, CLI, runtime
config, schema, seed, hooks, skills, identity YAMLs, and docs. No Portuguese
runtime paths remain outside migration-only code. 519 tests passing. Isolated
smoke test validated.

Key outcome: a stable English foundation for CV1 Pi Runtime.

Reference: [CV0 English Foundation](../project/roadmap/cv0-english-foundation/index.md)

---

### 2026-04-17 — Pi adoption spike complete

Technical investigation of `~/dev/workspace/mirror-pi` (Henrique's project).
Key findings: do not port wholesale — it is pre-English-migration. Port the
interface ideas (Pi session lifecycle, `.pi/` skeleton, mirror-logger extension)
against the current English core.

Implementation sequence and risks documented.

Reference: [Pi Runtime Adoption Spike](spikes/pi-runtime-adoption-2026-04-17.md)

---

### 2026-04-17 — Docs scaffold complete

Documentation hierarchy created: index, getting-started, project briefing,
decisions, roadmap (CV0 retrospective + CV1 epics), product principles, process
guide, worklog, and two spike docs.

Adopted planning style from Alisson Vale's `mirror-mind` repo:
CV → Epic → Story with `plan.md` + `test-guide.md` per story, breadcrumbs,
status tables, and narrative worklog.

Reference: [Mirror Mind Documentation Assessment](../../docs/mirror-mind-assessment.md)

---

### 2026-04-17 — CV1.E1 Shared Command Core complete

Mirror skill logic extracted from `.claude/skills/mm:mirror/run.py` into
`src/memory/skills/mirror.py`. The Claude skill is now a thin display wrapper.
`python -m memory mirror <subcommand>` and `python -m memory conversation-logger <subcommand>`
added to the unified CLI.

532 tests passing. ruff, pyright, git diff --check all clean.

Reference: [CV1.E1 Shared Command Core](../project/roadmap/cv1-pi-runtime/cv1-e1-shared-command-core/index.md)

---

### 2026-04-17 — CV1.E3 Pi Session Lifecycle complete

Extended `conversation-logger` with full Pi session lifecycle support:
`--interface pi` flag on `log-user`/`log-assistant`, `session-start`
(unmute + stale orphan close + Pi JSONL backfill + pending extraction),
`close_stale_orphans`, and `backfill_pi_sessions`.

Extraction tracking added to `ConversationService` via `metadata.extracted`
JSON field — no schema migration needed. 549 tests passing.

Reference: [CV1.E3 Pi Session Lifecycle](../project/roadmap/cv1-pi-runtime/cv1-e3-pi-session-lifecycle/index.md)

---

### 2026-04-17 — CV1.E2 Pi Skill Surface complete

Added `.pi/` skeleton: `settings.json`, `mm-mirror` thin wrapper calling
`memory.skills.mirror.main()`, `SKILL.md` user guide, and `mirror-logger.ts`
extension ported from mirror-pi with English runtime names. Added
`session-end-pi` CLI command and `backup` route to `__main__.py`.

552 tests passing.

Reference: [CV1.E2 Pi Skill Surface](../project/roadmap/cv1-pi-runtime/cv1-e2-pi-skill-surface/index.md)

---

### 2026-04-17 — CV1.E4 Pi Operational Validation complete

End-to-end smoke test against isolated DB (`MEMORY_DIR=/tmp/cv1-e4`). Pi session
ran `/mm-mirror`, extension logged all turns via `mirror-logger.ts`, `session-start`
triggered extraction, 1 memory extracted from `journal=mirror` conversation.
Production DB untouched (confirmed by checksum). 0 ERROR lines in mirror-logger.log.

Fixed bug: `mirror-logger.ts` hardcoded `~/.mirror/` instead of reading
`MEMORY_DIR` from environment — corrected with `_resolveMemoryDir()`.

CV1 done condition met: dual-interface (Claude Code + Pi), shared Python core,
all four epics complete, 552 tests passing.

Reference: [CV1.E4 Pi Operational Validation](../project/roadmap/cv1-pi-runtime/cv1-e4-pi-operational-validation/index.md)

---

## Next

- **CV6 (planned): Multi-User Onboarding, Identity Runtime Maturity, and Extensibility** — persona metadata/routing is now database-backed with CLI inspection/debug tooling. Boundary-audit and extension-model planning now identify `mirror-logger.ts` as core runtime integration and `review-copy` as the first reference-extension candidate. The old repo-local `meta/personas/engineer.yaml` artifact has been removed. Extension planning now goes further: the recommended long-term model is a user-home external skill registry under `~/.mirror/<user>/extensions/`, with validated `skill.yaml` manifests, explicit `ext:` / `ext-` namespacing, and `review-copy` as the first migration candidate. A concrete reference external-skill tree now exists at `examples/extensions/review-copy/`, the install/validate/inspect/sync flow is documented end-to-end, Pi now consumes installed external skills from the runtime catalog, Claude now has explicit project-surface expose/clean commands, and both repo-local `review-copy` skills have been removed. The former intelligence-depth track moves to CV7.
- **Follow-up: `MemoryClient` lifecycle sweep.** `__del__` is now a safety net, but hot call sites still open one client per call. Worth two follow-up passes:
  1. **Quick win (pending).** Apply the `mark_injected` pattern to the other `mirror_state.py` helpers (`_load_state`, `write_state`) that also open a fresh client on every call. Each hook invocation today runs bootstrap + migrations once per helper call; a shared client would halve or third that cost for common hook paths.
  2. **Structural.** Introduce a per-process `MemoryClient` cache keyed by `db_path` (lazy singleton) for library helpers in `hooks/` and `cli/conversation_logger.py`. Long-lived callers (Pi extension, shell hooks wired into one process) would reuse a single connection instead of paying bootstrap cost on every call. See [Decisions](../project/decisions.md) for the split between one-shot CLI entry points (process exit reclaims fds, no change needed) and library functions called from Python (where caching matters).

---

**See also:** [Roadmap](../project/roadmap/index.md) · [Decisions](../project/decisions.md)
