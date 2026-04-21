# Mirror Mind Operational Reference

Quick reference for Claude Code. Load on demand from `CLAUDE.md`.

---

## Personas

Personas are specialized lenses. They change depth and repertoire, not the core
voice. The mirror still speaks in first person as one ego.

| Persona | Domain | Inherits From |
|---------|--------|---------------|
| `writer` | Writing, articles, publishing | `self` |
| `marketer` | Marketing, social media, launch copy | `ego` |
| `mentor` | Mentoring, practical philosophy | `ego` |
| `therapist` | Therapy, existential questions, psychology, shadow | `self` |
| `thinker` | Intellectual sparring, ideas, concepts, hypotheses | `self` |
| `teacher` | Classes, instructional design, presentations | `ego` |
| `product-designer` | Product, UX, product strategy | `ego` |
| `engineer` | Software, tools, debugging, architecture | `ego` |
| `doctor` | Health, symptoms, medicine, lifestyle | `self` |
| `scholar` | General knowledge, curiosity, research framing | `ego` |
| `treasurer` | Finance, spending, balances, runway, budget | `ego` |
| `traveler` | Travel planning, destinations, logistics | `ego` |

**Files:** `~/.mirror/<user>/identity/personas/<name>.yaml`

---

## Journeys

Journeys are long-running arcs with identity, journey-path status, tasks,
memories, conversations, and attachments.

Journeys are loaded dynamically from the database. To list active journeys:

```python
mem.list_active_journeys()
```

**YAML files:** `~/.mirror/<user>/identity/journeys/<slug>.yaml`
**Database:** `identity` rows with `layer='journey'` and
`layer='journey_path'`

### Attachments By Journey

Attachments are long documents stored in the `attachments` table and linked to
a journey. They contain scripts, transcripts, articles, reference material, and
metadata that are not stored in the repository.

```python
# Semantic search inside one journey
results = mem.search_attachments("journey-id", "search terms", limit=3)

# Global attachment search when the journey is unknown
results = mem.search_all_attachments("search terms", limit=5)

# Read one attachment
attachment, score = results[0]
print(attachment.content)
```

Use attachments when the user asks about material associated with a journey:
episodes, scenes, characters, classes, research notes, scripts, transcripts, or
other long-form reference content.

---

## Skills

| Command | Purpose | Main Arguments |
|---------|---------|----------------|
| `/mm:mirror` | Loads identity, persona, journey, and attachments for Mirror Mode | `load [--persona P] [--journey J] [--query Q] [--org]`, `log "summary"`, `journeys` |
| `/mm:consult` | Asks other LLMs through OpenRouter with Mirror context | `<family> [tier] "prompt"`, `credits` |
| `/mm:review-copy` | Reference extension example for multi-LLM copy review; not a core framework capability | skill-driven workflow |
| `/mm:journeys` | Lists journeys with status | no arguments |
| `/mm:journey` | Shows detailed journey identity, journey path, memories, and conversations | `[journey]`, `update <journey> <content>` |
| `/mm:memories` | Lists or searches memories by type, layer, and journey | `--type T`, `--layer L`, `--journey J`, `--search "Q"`, `--limit N` |
| `/mm:tasks` | Manages tasks by journey | `list`, `add "title"`, `done <id>`, `doing <id>`, `block <id>`, `delete <id>`, `import`, `sync` |
| `/mm:week` | Weekly planning | `view`, `plan "text"`, `save` |
| `/mm:journal` | Records a personal journal entry | `[--journey J] "text"` |
| `/mm:save` | Exports conversation content to Markdown | `[slug]`, `--full`, `--session-id ID`, `--mirror-home PATH` |
| `/mm:recall` | Loads a previous conversation into context | `<conversation_id> [--limit N]` |
| `/mm:conversations` | Lists recent conversations | `--limit N`, `--journey J`, `--persona P` |
| `/mm:backup` | Backs up the memory database | no arguments |
| `/mm:seed` | Seeds identity files from the active user home into the database | no arguments |
| `/mm:mute` | Toggles conversation logging | no arguments |
| `/mm:new` | Starts a new conversation | no arguments |

Portuguese command aliases have been removed. Use English options such as
`--journey`.

---

## Database

**Default location (production):** `~/.mirror/<user>/memory.db`

Set via `MIRROR_HOME=~/.mirror/<user>` or `MIRROR_USER=<user>`. Dev and test
environments default to `~/.mirror-poc/memory_dev.db` and
`~/.mirror-poc/memory_test.db` unless overridden with `DB_PATH`.

Existing installs under legacy locations must be moved with an explicit
operational plan or pointed at with environment configuration.

### Legacy Migration Workflow

Use this when you have a Portuguese-era source database such as `memoria.db`
and want to migrate it into one explicit user home.

#### Supported source policy

Supported:
- clean Portuguese legacy databases

Rejected explicitly:
- already-English/current databases
- mixed Portuguese/English databases
- unsupported or ambiguous SQLite shapes

#### Commands

```bash
python -m memory migrate-legacy validate \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror/<user> \
  --report /tmp/mirror-migration-validate.json

python -m memory migrate-legacy run \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror/<user> \
  --report /tmp/mirror-migration-run.json
```

#### Safety guarantees

- explicit source required
- explicit target home required
- source is never mutated
- target `memory.db` must not already exist
- no silent merge into an existing target
- `validate` performs no writes
- `run` copies first, migrates the copy, and verifies the result

### Main Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `conversations` | Conversation sessions | id, title, persona, journey, started_at, ended_at |
| `messages` | Conversation messages | id, conversation_id, role, content, created_at |
| `memories` | Extracted or manual memories | id, memory_type, layer, title, content, journey, embedding |
| `identity` | Identity, personas, journeys, journey paths | id, layer, key, content, version |
| `attachments` | Journey knowledge base | id, journey_id, name, content, embedding |
| `tasks` | Tasks linked to journeys | id, journey, title, status, due_date, scheduled_at, source |
| `memory_access_log` | Reinforcement access log | memory_id, accessed_at |
| `conversation_embeddings` | Conversation summary embeddings | conversation_id, summary_embedding |
| `runtime_sessions` | Runtime session ↔ conversation registry (CV5) | session_id, conversation_id, interface, mirror_active, persona, journey, hook_injected, active, started_at, updated_at, closed_at |

### Runtime Session Model (CV5)

The authoritative mapping between a runtime `session_id` (Claude Code hook id or Pi session file path) and a `conversation_id` lives in `runtime_sessions`. Mirror Mode state (active, persona, journey, hook_injected) is stored per row, so two simultaneous sessions under the same mirror home can hold independent state.

Operational consequences:

- **Concurrent sessions are safe.** One mirror home can host several runtime sessions at once. Session creation, stale-orphan cleanup, and mirror state updates are all routed by explicit `session_id`.
- **Hooks must pass `--session-id`.** Claude Code hooks extract `session_id` from the hook payload; Pi uses the session file path. CLIs that change mirror state warn on stderr if `--session-id` is missing rather than silently no-op'ing.
- **No singleton files.** `current_session`, `mirror_state.json`, and `session_map.json` are gone; their runtime responsibilities moved into `runtime_sessions`. The only per-home flag file that remains is `mute`.

---

## Python API

```python
from memory import MemoryClient

mem = MemoryClient()  # default environment comes from MEMORY_ENV
```

### Conversations

- `mem.start_conversation(interface, persona=, journey=, title=)` -> `Conversation`
- `mem.add_message(conversation_id, role, content)` -> `Message`
- `mem.end_conversation(conversation_id, extract=True)` -> `list[Memory]`

### Memories

- `mem.add_memory(title, content, memory_type, layer="ego", journey=, tags=)` -> `Memory`
- `mem.add_journal(content, journey=)` -> `Memory`
- `mem.search(query, limit=5, memory_type=, layer=, journey=)` -> `list[(Memory, score)]`

### Identity And Journeys

- `mem.get_identity(layer, key)` -> `str | None`
- `mem.set_identity(layer, key, content)` -> `Identity`
- `mem.get_journey_path(journey)` -> `str`
- `mem.set_journey_path(journey, content)` -> `Identity`
- `mem.list_active_journeys()` -> `list[dict]`
- `mem.detect_journey(query)` -> `list[(id, score, match_type)]`
- `mem.get_journey_status(journey=None)` -> `dict`
- `mem.load_mirror_context(persona=, journey=, org=False, query=)` -> `str`

### Tasks

- `mem.add_task(title, journey=, due_date=, scheduled_at=, stage=, source="manual")` -> `Task`
- `mem.complete_task(task_id)` -> `None`
- `mem.list_tasks(journey=, status=, open_only=True)` -> `list[Task]`
- `mem.import_tasks_from_journey_path(journey)` -> `list[Task]`

### Attachments

- `mem.add_attachment(journey_id, name, content)` -> `Attachment`
- `mem.search_attachments(journey_id, query, limit=3)` -> `list[(Attachment, score)]`
- `mem.search_all_attachments(query, limit=5)` -> `list[(Attachment, score)]`

Portuguese API compatibility wrappers have been removed. Use the English names
above.

---

## External Tools And Extensions

Domain-specific tools that need their own storage, importers, APIs, or highly
specialized workflows should live outside Mirror Mind core and provide context
back as text, attachments, explicit prompts, or skill-orchestrated command
flows.

Mirror Mind may temporarily ship some **reference extensions** in-repo while the
extension model matures. These examples are not core framework capabilities even
when they are available as skills.

Current reference path:

```text
examples/extensions/review-copy/
  skill.yaml
  SKILL.md
```

Installed user-home shape:

```text
~/.mirror/<user>/extensions/review-copy/
  skill.yaml
  SKILL.md
```

Runtime names:
- Claude Code: `ext:review-copy`
- Pi: `ext-review-copy`

List, validate, inspect, sync, install, and uninstall manifests with:

```bash
python -m memory list extensions --extensions-root examples/extensions
python -m memory extensions list --extensions-root examples/extensions --runtime pi
python -m memory extensions validate --extensions-root examples/extensions
python -m memory extensions validate --mirror-home ~/.mirror/<user>
python -m memory inspect extension review-copy --extensions-root examples/extensions
python -m memory inspect extension review-copy --mirror-home ~/.mirror/<user>
python -m memory inspect runtime-catalog pi --mirror-home ~/.mirror/<user>
python -m memory extensions sync --extensions-root examples/extensions --runtime pi --target-root /tmp/pi-skills
python -m memory extensions sync --extensions-root examples/extensions --runtime claude --target-root /tmp/claude-skills
python -m memory extensions install review-copy --extensions-root examples/extensions --mirror-home ~/.mirror/<user>
python -m memory extensions install review-copy --extensions-root examples/extensions --mirror-home ~/.mirror/<user> --runtime pi
python -m memory extensions uninstall review-copy --mirror-home ~/.mirror/<user>
python -m memory extensions uninstall review-copy --mirror-home ~/.mirror/<user> --runtime pi
```

`sync` copies runtime-visible `SKILL.md` files into one explicit target root and
writes an `extensions.json` catalog there. This keeps installation explicit and
avoids implicit mutation of repo-local skill surfaces.

`extensions.json` v1 contains:
- `schema_version`
- `runtime`
- `target_root`
- `generated_at`
- `extensions[]`

Each extension entry includes both logical metadata (`id`, `name`, `kind`,
`summary`, `command_name`) and filesystem metadata (`source_extension_dir`,
`manifest_path`, `source_skill_path`, `installed_skill_path`).

Concrete `review-copy` migration flow:

Preferred one-command install:

```bash
python -m memory extensions install \
  review-copy \
  --extensions-root examples/extensions \
  --mirror-home ~/.mirror/<user>
```

To install only one runtime surface, add `--runtime pi` or `--runtime claude`.
To remove the extension later, run:

```bash
python -m memory extensions uninstall review-copy --mirror-home ~/.mirror/<user>
```

Equivalent explicit step-by-step flow:

```bash
mkdir -p ~/.mirror/<user>/extensions
cp -R examples/extensions/review-copy ~/.mirror/<user>/extensions/

python -m memory extensions validate --mirror-home ~/.mirror/<user>
python -m memory inspect extension review-copy --mirror-home ~/.mirror/<user>

python -m memory extensions sync \
  --mirror-home ~/.mirror/<user> \
  --runtime pi \
  --target-root ~/.mirror/<user>/runtime/skills/pi

python -m memory extensions sync \
  --mirror-home ~/.mirror/<user> \
  --runtime claude \
  --target-root ~/.mirror/<user>/runtime/skills/claude
```

Expected artifacts:
- `~/.mirror/<user>/extensions/review-copy/skill.yaml`
- `~/.mirror/<user>/extensions/review-copy/SKILL.md`
- `~/.mirror/<user>/runtime/skills/pi/ext-review-copy/SKILL.md`
- `~/.mirror/<user>/runtime/skills/claude/ext:review-copy/SKILL.md`
- one `extensions.json` catalog per runtime target root

The in-repo `mm:review-copy` / `mm-review-copy` skill remains a temporary
reference extension while migration guidance stabilizes.

Financial tooling lives in `~/dev/workspace/financial-tools`. The `treasurer`
persona can interpret financial context from that tool, but Mirror Mind does
not import bank statements or own financial tables.

---

## Common SQL

```sql
-- Recent memories
SELECT title, memory_type, layer, created_at
FROM memories
ORDER BY created_at DESC
LIMIT 10;

-- Open tasks
SELECT title, journey, status, due_date
FROM tasks
WHERE status != 'done'
ORDER BY due_date;

-- Recent conversations with message counts
SELECT c.title, c.persona, c.journey, c.started_at,
  (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) AS messages
FROM conversations c
ORDER BY c.started_at DESC
LIMIT 10;
```

---

## Memory Types

| Type | Description |
|------|-------------|
| `decision` | Operational or strategic decision |
| `insight` | New realization or understanding |
| `idea` | Concept for future implementation |
| `journal` | Journal entry or personal reflection |
| `tension` | Internal conflict or psychological tension |
| `learning` | Technical or relational learning |
| `pattern` | Recurring observed pattern |
| `commitment` | Commitment made by the user |
| `reflection` | Deeper reflection about identity or purpose |

**Layers:** `self`, `ego`, `shadow`, `persona`, `journey`, `journey_path`

---

## File Architecture

```text
templates/identity/              -> generic bootstrap templates shipped in the repo
~/.mirror/<user>/identity/       -> real user-owned identity files
~/.mirror/<user>/memory.db       -> runtime source of truth
src/memory/                      -> Python package: client, store, db, search, extraction, tasks, llm_router
.claude/skills/                  -> operational skills (mm:mirror, mm:tasks, etc.)
.pi/skills/                      -> Pi skills
```

### Templates Vs. Real Content

Repository templates under `templates/identity/` are bootstrap assets only.
The active user home under `~/.mirror/<user>/identity/` is the seed source for
real identity. The memory database is the runtime source of truth for personal
identity content.

```python
from memory import MemoryClient

mem = MemoryClient()

soul = mem.get_identity("self", "soul")
ego_identity = mem.get_identity("ego", "identity")
ego_behavior = mem.get_identity("ego", "behavior")
user_profile = mem.get_identity("user", "profile")
org = mem.get_identity("organization", "identity")
persona = mem.get_identity("persona", "mentor")
journey = mem.get_identity("journey", "my-journey")
journey_path = mem.get_journey_path("my-journey")
```

**Rule:** do not read repository templates directly to obtain personal runtime content.
Use the active user home for seed input, and use the database through `MemoryClient`
for runtime content.

---

## Transcript Export

`python -m memory save` is now aligned with the user-home/export model.

Examples:

```bash
python -m memory save my-session
python -m memory save --full my-session
python -m memory save --session-id $CLAUDE_SESSION_ID my-session
python -m memory save --mirror-home ~/.mirror/<user> my-session
```

Output resolution priority:
1. explicit output dir, when provided by the export layer
2. explicit `--mirror-home` → `<mirror-home>/exports/transcripts`
3. configured `TRANSCRIPT_EXPORT_DIR`

Transcript export is explicit by default. Automatic transcript export remains
controlled by `TRANSCRIPT_EXPORT_AUTOMATIC`.

## Migration Reports

Both legacy migration commands support:

- `--report PATH`

The report is written as JSON and includes:
- generation timestamp
- command mode (`validate` or `run`)
- source and target paths
- source classification
- source row counts
- applied migrations
- detected legacy columns, indexes, and identity layers
- planned translations
- copied sidecars for `run`
- post-migration verification details for `run`

## Configuration

`.env` is loaded automatically by `memory.config` at import time; values
already present in the real environment take precedence (setdefault).

Two starter files live at the repo root:

- `.env.example` — minimal template (identity + API keys).
- `.env.example.advanced` — canonical reference with every knob documented.

The full environment surface:

### Identity (CV4 user home)

| Variable | Default | Role |
|----------|---------|------|
| `MIRROR_HOME` | (unset) | Explicit path to the user's mirror home. Takes precedence over `MIRROR_USER`. |
| `MIRROR_USER` | (unset) | Short user name; resolves to `~/.mirror/<user>`. |

In production, one of the two must be set. Setting both is only valid when
they agree (`MIRROR_HOME` ends with the same user name).

### API keys

| Variable | Role |
|----------|------|
| `OPENAI_API_KEY` | Embeddings (`text-embedding-3-small`). |
| `OPENROUTER_API_KEY` | Extraction (Gemini Flash) and the multi-LLM `consult` command. |

### Environment selection

| Variable | Default | Role |
|----------|---------|------|
| `MEMORY_ENV` | `production` | One of `production`, `development`, `test`. Controls DB file name and gates `MemoryClient.reset`. |

### Transcript export (CV4.E6)

| Variable | Default | Role |
|----------|---------|------|
| `TRANSCRIPT_EXPORT_AUTOMATIC` | `false` | When true, session-end automatically exports the full transcript. Accepts `1`, `true`, `yes`, `on`. |

### Path overrides

All of these derive from `MIRROR_HOME` in production. Set them only to
override the default layout.

| Variable | Default | Role |
|----------|---------|------|
| `MEMORY_DIR` | `MIRROR_HOME` (prod) or `~/.mirror-poc` | Runtime working dir for `mute` and `.bootstrap.lock`. |
| `MEMORY_PROD_DIR` | `MEMORY_DIR` | Production-only override. |
| `DB_PATH` | `<MIRROR_HOME>/memory.db` | Full SQLite path. |
| `DB_BACKUP_PATH` | `<DB_PATH parent>/backups` | Legacy alias for `BACKUP_DIR`. |
| `BACKUP_DIR` | `<MIRROR_HOME>/backups` | `memory backup` output. |
| `EXPORT_DIR` | `<MIRROR_HOME>/exports` | Markdown export root (`save`, `week`, …). |
| `TRANSCRIPT_EXPORT_DIR` | `<EXPORT_DIR>/transcripts` | Full-transcript export dir. |

### Runtime integrations

| Variable | Default | Role |
|----------|---------|------|
| `PI_SESSIONS_DIR` | `~/.pi/agent/sessions` | Source directory for `backfill_pi_sessions`. Override for multi-user-on-one-machine. |
| `MIRROR_SESSION_ID` | (unset) | Fallback session id for conversation-logger CLIs when neither `--session-id` nor a hook payload is present. Rarely set by humans. |

### Set by external runtimes (do not set manually)

- `CLAUDE_PROJECT_DIR` — injected by Claude Code when it invokes hooks.
- Claude Code hook payloads carry `session_id` on stdin.
- Pi's extension passes the session file path to the logger CLI.

---

## Hybrid Search

```text
score = 0.6 * semantic_similarity
      + 0.2 * recency
      + 0.1 * reinforcement
      + 0.1 * manual_relevance
```

Embeddings: OpenAI `text-embedding-3-small` with 1536 dimensions.
