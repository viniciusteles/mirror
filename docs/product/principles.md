[< Docs](../index.md)

# Principles

Guidelines for product behavior, code architecture, testing, and process.
Organized by domain so you can find what is relevant to your current work.

---

## Product

**First-person voice.**  
The mirror speaks as the active user, not about them. Every response is in first person,
from their worldview, reflecting their philosophy. "You should consider..." is wrong.
"I lean toward..." is right.

**Memory as intelligence.**  
Conversations that vanish are waste. Every conversation that ends with a
journey set and enough messages should produce memories. The memory bank is not
a log — it is an intelligence layer. Quality matters more than quantity.

**Journeys as continuity.**  
Nothing important should be re-explained. If a topic has a journey, the mirror
loads that context automatically. The mirror is not a stateless assistant — it
carries terrain.

**Interfaces are thin.**  
Claude Code and Pi call the same Python core. Neither interface owns behavior.
If behavior is in a skill script, it belongs in `src/memory/skills/` — not in
the interface layer.

**One voice, many lenses.**  
Personas are not separate agents. The ego activates a persona; the voice stays
unified. The persona adds depth without becoming a different entity.

**Doing as entry, being as discovery.**  
For software audiences, the front door should be concrete work: projects,
Builder, coherence, lenses, and agentic execution. The identity layer should not
be removed, but it should not always be the public promise. Maestro can attract
through doing while Mirror reveals itself through use. The user buys operational
power and later discovers continuity, memory, personas, journeys, and inner
sensemaking as the work deepens.

---

## Code

**Service layer is the architecture.**  
`MemoryClient` is a façade. Services (`ConversationService`, `JourneyService`,
etc.) are the implementation. `Store` handles persistence. Import direction is
one way: `cli` and `hooks` import from `services`; `services` import from
`storage`; `storage` imports from `db`. Never reverse this.

**English everywhere.**  
Variable names, function names, CLI commands, schema columns, identity layer
keys, commit messages, and documentation are all English. The only exceptions
are user-authored content (journal entries, journey descriptions) and
migration-only code that handles old schemas.

**No logic in interfaces.**  
Skill scripts (`.claude/skills/`, `.pi/skills/`) are entry points. They may
parse arguments and call `sys.exit`, but they do not contain business logic.
Logic belongs in `src/memory/skills/` or the relevant service.

**Small, focused modules.**  
One module, one responsibility. `conversation.py` handles conversation
lifecycle. `extraction.py` handles LLM extraction. `search.py` handles hybrid
search. Do not grow a module sideways — extract a new one.

**Explicit over implicit.**  
Production database mutations require explicit confirmation. Extraction
requires explicit guard conditions (journey + ≥4 messages). The system does
not guess; it requires.

---

## Testing

**Unit tests mock I/O, never hit real APIs.**  
The CI must pass without `OPENAI_API_KEY` or `OPENROUTER_API_KEY`. Unit tests
mock embedding generation and LLM extraction. If a test calls a real API, it is
an integration test and must be explicitly marked as such.

**Integration tests hit a real SQLite file.**  
The test database is `memory_test.db` under `MEMORY_DIR`. Integration tests use
`MEMORY_ENV=test`. They are not mocked — they exercise real database reads and
writes.

**Smoke tests use an isolated environment.**  
End-to-end validation uses a temporary `HOME` and explicit `MEMORY_DIR` to
prevent touching the production database. The environment variables must be set
to empty strings before subprocess invocation to prevent `.env` from repopulating
them.

**Coverage is pragmatic.**  
The current threshold is 40%. This is deliberately low — the system has complex
I/O-heavy paths that are expensive to test fully. Raise the threshold as the
core stabilizes and coverage gaps are closed intentionally.

**Every story ends with a concrete verification moment.**  
The test guide for a story is not a description — it is a sequence of
copy-paste-runnable commands with expected output. Someone should be able to
run through it without reading the plan.

---

## Process

**Design before code.**  
For non-trivial work: explore the codebase, design the approach, present for
approval. The plan becomes the story doc. Only then write code.

**TDD by default.**  
Tests exist before marking a story done. For behavior changes, tests come
first. The CI gate is the minimum bar — it does not substitute for judgment
about test quality.

**Small stories, concrete verification.**  
A story should be completable in one session. If it cannot be verified
end-to-end at the end of the session, it is too large — split it.

**Docs updated in the same cycle.**  
When code changes: update the relevant docs in the same commit or the same PR.
Docs that describe a state the code no longer reflects are worse than no docs.

**Refactoring evaluated in-cycle.**  
When a story is done, ask: what design debt did we accumulate? What can we clean
now without breaking scope? Refactoring is not a separate track — it is part of
delivery. Document what was done or consciously deferred in `refactoring.md`.

**Commits stay small and English.**  
One concern per commit. Descriptive English message. No `fix stuff`, no
`WIP`, no Portuguese names in commit messages.

**Push only when asked.**  
The driver does not push to the remote unless the user explicitly requests it.

---

**See also:** [Briefing](../project/briefing.md) · [Development Guide](../process/development-guide.md)
