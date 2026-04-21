# Mirror Mind

Every time you open a new AI session, you start from zero.

You re-explain your projects. You re-establish your context. You repeat your values, your constraints, your situation — again. And the AI, no matter how capable, responds as if it's meeting you for the first time. Because it is.

The advice it gives could fit anyone. It doesn't know that you made that decision three months ago and why. It doesn't know what you're navigating right now, what tensions are unresolved, what you committed to last week. It answers in a vacuum.

That's not an assistant. That's a very smart stranger.

**Mirror Mind is a different bet.** It's a framework that turns Claude into an AI that *actually knows you* — your identity, your voice, your values, your ongoing projects — and accumulates that knowledge over time, conversation by conversation.

The mirror doesn't just answer your questions. It reflects your own intelligence back at you, sharpened. It remembers what matters. It carries context across months. It knows where you are in your projects and what's unresolved. When you need a therapist's depth, it shifts. When you need an engineer's precision, it shifts. One unified voice, multiple lenses.

**What changes when you adopt Mirror Mind:**

- **No more re-explaining yourself.** Your identity, values, and projects are loaded into every conversation automatically.
- **Your insights stop disappearing.** Every conversation is analyzed by an LLM and meaningful memories — decisions, insights, tensions, commitments — are extracted and stored with semantic search.
- **The AI speaks as you, not about you.** In first person. From your worldview. Reflecting your philosophy back at you.
- **Your projects have continuity.** Journeys give the mirror ongoing context about what you're navigating — what stage you're at, what's been decided, what's next.
- **Multiple intelligences, one voice.** A therapist lens for existential questions. A strategist for business decisions. A writer for content. Each activated automatically by context, never breaking character.
- **Second opinions with your identity intact.** Consult Gemini, GPT, Grok or DeepSeek — all with your identity injected into the prompt, so external perspectives don't lose your context.

The architecture is Jungian by design: Self, Ego, Personas, Shadow. Not as decoration — as a genuine model of how a person's psyche operates across different domains and depths.

This is not a chatbot. It's a mirror — conscious, accumulative, and yours.

## How it works

The project uses [Claude Code](https://docs.anthropic.com/en/docs/claude-code) as the primary interface. Mirror Mind now separates repository templates from live user identity:

```text
templates/identity/           → Generic bootstrap templates shipped in the repo
~/.mirror/<user>/identity/    → Real user-owned identity
~/.mirror/<user>/memory.db    → Runtime source of truth
src/memory/                   → Long-term memory system (Python)
.claude/skills/               → Operational skills (mirror, consult, journey, etc.)
```

The identity itself is still layered psychologically:

```text
self/            → Soul and purpose (deepest identity)
ego/             → Behavior, tone, and operational identity
personas/        → Domain specialists (your custom lenses)
user/            → Your profile
organization/    → Your organization's identity
journeys/        → Journeys — projects and life arcs where things happen
```

Personas are not separate entities — they are specialized lenses the ego activates based on context. The voice is always one.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (package manager)

## Quick start

```bash
# Clone the repository
git clone https://github.com/viniciusteles/mirror-poc.git
cd mirror-poc

# Install Python dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your keys:
#   OPENAI_API_KEY=...                 (embeddings)
#   OPENROUTER_API_KEY=...             (multi-LLM)
#   MEMORY_ENV=production              (optional environment)
#   MIRROR_HOME=~/.mirror/your-name    (recommended user home)
#   MIRROR_USER=your-name              (optional convenience/consistency check)
#   DB_PATH=...                        (compatibility override)
#   DB_BACKUP_PATH=...                 (compatibility override)
```

## Setting up your identity

Mirror Mind is a framework — it ships with generic templates. Your real identity lives in your user home, not in the repository.

### 1. Initialize your user home

```bash
python -m memory init your-name
```

This copies the repository templates into:

```text
~/.mirror/your-name/identity/
```

### 1a. Migrate a legacy Portuguese-era database if needed

If you already have a legacy database such as `~/.espelho/memoria.db`, use the
explicit migration workflow before normal runtime use:

```bash
python -m memory migrate-legacy validate \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror/your-name \
  --report /tmp/mirror-migration-validate.json

python -m memory migrate-legacy run \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror/your-name \
  --report /tmp/mirror-migration-run.json
```

Safety contract:
- explicit source required
- explicit target home required
- source is never mutated
- target `memory.db` must not already exist
- only clean Portuguese-era legacy DBs are supported in this flow
- mixed-state or already-English DBs fail explicitly

### 2. Define your soul and ego

Edit the YAML files in your user home:

- **`~/.mirror/your-name/identity/self/soul.yaml`** — Who you are at the deepest level. Purpose, values, worldview.
- **`~/.mirror/your-name/identity/ego/identity.yaml`** — Your operational identity. What you do, how you present yourself.
- **`~/.mirror/your-name/identity/ego/behavior.yaml`** — Tone and style rules. How the mirror should speak.
- **`~/.mirror/your-name/identity/user/identity.yaml`** — Your profile: name, role, background.
- **`~/.mirror/your-name/identity/organization/identity.yaml`** — Your company or project (optional).

### 3. Create your personas

Copy `~/.mirror/your-name/identity/personas/_template.yaml` for each domain you want a specialized lens.

Edit each file with the persona's identity, approach, and routing keywords. Personas inherit from `ego` (behavior) or `self` (full soul) depending on depth.

### 4. Create your journeys

Copy `~/.mirror/your-name/identity/journeys/_template.yaml` for each ongoing journey.

A journey is any project, arc, or area of your life where things are happening and the mirror needs context. See [Journeys](#journeys) below.

### 5. Populate the memory bank

```bash
claude
```

Then inside Claude Code:

```
/mm:seed
```

This loads identity from the active user home into the memory database. The mirror reads from the database at runtime; the user-home YAMLs are the seed source.

### 6. Configure routing in CLAUDE.md

Edit `CLAUDE.md` to map your personas to domains:

```markdown
**Routing by domain:**
- Writing/blog/articles → `writer`
- Therapy/existential/psychology → `therapist`
- Student questions/mentoring → `mentor`
- Finance/budget/expenses → `treasurer` (with external financial context when available)
```

### 7. Start using

```
claude
```

Just talk. The mirror will route to the right persona automatically based on your message. If routing fails, use `/mm:mirror` explicitly.

## Commands

| Command | What it does |
|---------|-------------|
| `/mm:mirror` | Activates mirror mode — loads identity, persona, attachments and responds as you |
| `/mm:consult` | Consults other LLMs via OpenRouter with mirror context |
| `/mm:journey` | Status of active journeys |
| `/mm:journeys` | Quick list of all journeys |
| `/mm:memories` | List stored memories (insights, ideas, decisions) |
| `/mm:tasks` | Task management by journey |
| `/mm:week` | Weekly planning (ingest free-form text or view week) |
| `/mm:journal` | Record a personal journal entry |
| `/mm:backup` | Backup the memory database |
| `/mm:seed` | Seed identity from the active user home into the memory bank |
| `/mm:mute` | Toggle conversation recording (for testing) |
| `/mm:new` | Start a new conversation |
| `/mm:help` | List available commands |

### Reference extensions

Some useful capabilities may ship in-repo temporarily as **reference
extensions** while the extension model matures. These are not part of Mirror
Mind core even if they are available as skills.

Current example:
- `mm:review-copy` / `mm-review-copy` — a specialized multi-LLM copy review
  workflow kept in-repo as a reference extension, not as a core framework
  capability
- `examples/extensions/review-copy/` — the first external-skill reference tree,
  using `skill.yaml` plus `SKILL.md` with runtime names `ext:review-copy` and
  `ext-review-copy`

## Legacy migration

Mirror Mind now includes an explicit migration path for Portuguese-era databases.

### Supported source policy

`python -m memory migrate-legacy ...` supports only:
- clean Portuguese legacy databases such as `memoria.db`

It rejects:
- already-English/current databases such as `memory.db`
- mixed Portuguese/English database states
- ambiguous or unsupported SQLite shapes

### Commands

```bash
python -m memory migrate-legacy validate \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror/your-name \
  --report /tmp/mirror-migration-validate.json

python -m memory migrate-legacy run \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror/your-name \
  --report /tmp/mirror-migration-run.json
```

### What `validate` does

- classifies the source DB
- reports detected legacy columns, indexes, and identity layers
- reports planned translations such as:
  - `travessia -> journey`
  - `travessia_id -> journey_id`
  - `caminho -> journey_path`
- performs no writes

### What `run` does

- copies the source DB into `<target-home>/memory.db`
- copies SQLite sidecars when present
- runs the normal DB migration path on the copied target
- verifies the target now uses the English schema
- preserves source row counts
- never mutates the source DB

## Architecture

### Psychic layers (Jungian)

- **Self/Soul** — Deep identity, purpose, frequency. The unchanging core.
- **Ego** — Operational identity and behavior. How the self manifests day-to-day.
- **Personas** — Specialized expressions of the ego in specific domains.
- **Shadow** (planned) — Detection of unconscious patterns.

### Journeys

A generic AI knows nothing about your life. It answers in a vacuum. The mirror is different — it carries context about what you're going through.

A **journey** is any ongoing arc where the mirror needs to understand where you are, where you've been, and where you're headed. It can be:

- A project (building a product, writing a book)
- A life phase (career transition, financial restructuring)
- A practice (philosophical growth, health journey)
- A creative endeavor (a podcast series, a course)

Each journey has:
- **Identity** — what it is, why it matters, what stage it's in
- **Journey path** — a living status document, updated as things evolve
- **Memories** — insights, decisions, and ideas extracted from conversations
- **Tasks** — concrete next steps
- **Attachments** — reference documents the mirror can search semantically

When you talk to the mirror about a topic that relates to a journey, it loads that context automatically. The mirror doesn't just know who you are — it knows what you're navigating.

This is what makes the mirror a **conscious** reflection rather than a stateless assistant. Your journeys are the terrain; the mirror walks it with you.

### Memory system (`memory/`)

Long-term memory with semantic search. Stores conversations, extracts memories via LLM, and offers hybrid search (cosine similarity + recency + reinforcement).

- **Database:** SQLite at `~/.mirror/<user>/memory.db` in production
- **Database path:** configurable with `DB_PATH`
- **Backups:** `/mm:backup` zips the configured database into `DB_BACKUP_PATH`
- **Embeddings:** OpenAI text-embedding-3-small
- **Extraction:** Gemini Flash via OpenRouter
- **Search:** Hybrid scoring (4 signals)

### Memory layers

- `self` → Deep realizations about identity, purpose, values
- `ego` → Operational decisions, strategy, daily knowledge
- `shadow` → Tensions, avoided themes, recurring blind spots
- `persona` → Domain-specific operational knowledge

### External tools and extensions

Mirror Mind keeps the memory and identity framework separate from domain-specific
tools. When a domain needs its own database, importers, APIs, or a highly
specialized workflow, that capability should usually live outside Mirror Mind
core and provide context back to the mirror.

Typical extension boundaries:
- external tools with their own storage or APIs
- custom/user-installed skills that orchestrate stable core commands
- reference extensions kept in-repo temporarily for documentation and migration
  purposes

First reference external-skill tree:

```text
examples/extensions/review-copy/
  skill.yaml
  SKILL.md
```

Install shape for a real user home:

```text
~/.mirror/<user>/extensions/review-copy/
  skill.yaml
  SKILL.md
```

You can list, validate, inspect, sync, install, and uninstall example or user-home manifests with:

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

`sync` materializes runtime-visible skill folders such as:
- `/tmp/pi-skills/ext-review-copy/SKILL.md`
- `/tmp/claude-skills/ext:review-copy/SKILL.md`

and writes an `extensions.json` runtime catalog into the target root.

Pi consumption prototype:
- on `session_start`, `.pi/extensions/mirror-logger.ts` now reads the installed
  Pi runtime catalog when present
- validates the runtime catalog envelope
- logs discovered external skill commands
- shows a lightweight `ext N` status hint in the Pi UI
- on `resources_discover`, it contributes installed external `SKILL.md` paths
  from the Pi runtime catalog so those skills become part of Pi's discovered
  skill surface

Catalog shape (v1):
- `schema_version`
- `runtime`
- `target_root`
- `generated_at`
- `extensions[]`

Each extension entry records:
- `id`, `name`, `category`, `kind`, `summary`
- `runtime`, `command_name`
- `source_extension_dir`, `manifest_path`, `source_skill_path`
- `installed_skill_path`

### Concrete `review-copy` migration flow

One-command install into a real user home:

```bash
python -m memory extensions install \
  review-copy \
  --extensions-root examples/extensions \
  --mirror-home ~/.mirror/<user>
```

This installs the source tree under `~/.mirror/<user>/extensions/` and syncs
runtime-facing skill trees under `~/.mirror/<user>/runtime/skills/`.

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

Resulting artifacts:

```text
~/.mirror/<user>/extensions/review-copy/skill.yaml
~/.mirror/<user>/extensions/review-copy/SKILL.md
~/.mirror/<user>/runtime/skills/pi/ext-review-copy/SKILL.md
~/.mirror/<user>/runtime/skills/pi/extensions.json
~/.mirror/<user>/runtime/skills/claude/ext:review-copy/SKILL.md
~/.mirror/<user>/runtime/skills/claude/extensions.json
```

This keeps the source extension user-owned under `~/.mirror/<user>/extensions/`
while making runtime surfacing explicit and reproducible.

Financial import/reporting tools live in `~/dev/workspace/financial-tools`. The
`treasurer` persona can interpret financial context from that tool, but Mirror
Mind does not import bank statements or own financial tables.

## Stack

- **Python 3.10+** — memory and automation (managed with [uv](https://docs.astral.sh/uv/))
- **SQLite** — memory bank at `~/.mirror/<user>/memory.db`
- **OpenAI** — embeddings (text-embedding-3-small)
- **OpenRouter** — multi-LLM access (Gemini, GPT, Claude, etc.)
- **Claude Code** — primary interface

## Principles

- **First person** — the AI speaks as you, not about you

## License

MIT
