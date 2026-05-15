# Mirror Mind

![Before and after illustration: a person faces an opaque AI mirror that cannot reflect them, then a polished Mirror Mind reflection that carries their identity, memory, projects, and preferences.](docs/assets/mirror-mind-before-after-cartoon-600px.jpg)

Every time you open a new AI session, you start from zero.

You re-explain your projects. You re-establish your context. You repeat your values, your constraints, your situation — again. And the AI, no matter how capable, responds as if it's meeting you for the first time. Because it is.

The advice it gives could fit anyone. It doesn't know that you made that decision three months ago and why. It doesn't know what you're navigating right now, what tensions are unresolved, what you committed to last week. It answers in a vacuum.

That's not an assistant. That's a very smart stranger.

**Mirror Mind is a different bet.** It is a local-first memory and identity framework for agentic AI runtimes. It gives each session access to your identity, voice, values, journeys, projects, and accumulated memory, so work can continue without starting from zero. The system is not a generic chatbot layer. It is Mirror Core: the architecture that lets Pi, Claude Code, Gemini CLI, and Codex operate with continuity, context, and coherence.

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

## Origins and credits

Mirror Mind is a continuation of the original mirror work created by **Alisson Vale**.

This repository builds on that original idea and implementation. The work here extends it in several important directions: making the system usable for people who do not speak Portuguese, adding a Pi-based multi-model runtime, and hardening the framework for multi-user and multi-session use. The original mirror concept and the first `mirror-poc` implementation are Alisson's, and this repository should be understood as a continuation and expansion of that foundation.

The move toward **Pi** as a runtime was inspired by **Henrique Bastos** and his early work in
[henriquebastos/mirror-mind](https://github.com/henriquebastos/mirror-mind).
That work showed a strong path toward a more model-flexible runtime, and it directly influenced the adoption of Pi here.

Historically, **Claude Code was the initial harness** used in Alisson's original implementation. Over time, this continuation adopted Pi as the preferred runtime because it makes the mirror less tied to one model/provider and better aligned with a multi-model future.

## How it works

Mirror Mind now supports four runtimes:
- **Pi** — the preferred interface today, because it makes the mirror multi-model and less tied to a single provider/runtime
- **Gemini CLI** — fully supported with the same shell-hook model as Claude Code; L4 full parity
- **Codex** — supported at L3 parity via wrapper script, JSONL backfill, `AGENTS.md`, and `$mm-*` skill invocation
- **Claude Code** — the original interface used by Alisson's first implementation, still supported as an alternative

Mirror Mind separates repository templates from live user identity:

```text
src/memory/                   → Long-term memory system (Python)
templates/identity/           → Generic bootstrap templates shipped in the repo
examples/extensions/          → Reference extensions (e.g. review-copy)
tests/                        → Automated tests
.claude/skills/               → Operational skills (Claude Code)
.pi/skills/                   → Operational skills (Pi)
.gemini/hooks/                → Lifecycle hooks (Gemini CLI)
.agents/skills/               → Shared operational skills for Gemini CLI and Codex — symlinked from .pi/skills/
~/.mirror/<user>/identity/    → Real user-owned identity (outside the repo)
~/.mirror/<user>/memory.db    → Runtime source of truth (outside the repo)
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

## What you'll need

Mirror Mind requires accounts at two separate services before anything works:

**1. [OpenRouter](https://openrouter.ai) — for embeddings, memory extraction, and multi-LLM**
Create an account, add credits, and generate an API key. OpenRouter handles everything the memory system needs: generating embeddings to index and search your memories (using OpenAI’s text-embedding-3-small model behind the scenes), extracting memories from conversations via Gemini Flash, and the `/mm-consult` command to query other models. Cost is very low — a few cents per session.

**2. An AI provider subscription — to run the mirror**
Mirror Mind is a framework; the actual AI conversation runs through Pi, Gemini CLI, Codex, or Claude Code:
- **Pi** is model-agnostic — you can configure any supported model, but you need access to whichever one you choose
- **Gemini CLI** uses Gemini models; requires a Google account (free tier available)
- **Codex** is agent-native and model-flexible; supported at L3 parity
- **Claude Code** requires a Claude subscription (claude.ai Pro or Anthropic API access)

One account for infrastructure, one for the conversation interface. Both are required.

## Prerequisites

- [Pi](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) — preferred runtime (multi-model, not locked to one provider)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) — fully supported runtime (`brew install gemini-cli`)
- [Codex](https://github.com/google-gemini/codex) — supported runtime
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — supported alternative runtime
- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — package manager

## Quick start

```bash
# Clone the repository
git clone https://github.com/viniciusteles/mirror.git
cd mirror

# Install Python dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your keys:
#   OPENROUTER_API_KEY=...             (embeddings, extraction, and multi-LLM)
#   MEMORY_ENV=production              (optional environment)
#   MIRROR_HOME=~/.mirror/your-name    (recommended user home)
#   MIRROR_USER=your-name              (optional convenience/consistency check)
#   DB_PATH=...                        (compatibility override)
#   DB_BACKUP_PATH=...                 (compatibility override)
```

For a more detailed walkthrough — including verification steps and an onboarding checklist — see [Getting Started](docs/getting-started.md).

## Setting up your identity

Mirror Mind ships with opinionated, ready-to-use identity templates. Your name
is the only input required — no YAML editing needed before the first session.

### 1. Initialize your user home

```bash
uv run python -m memory init your-name
```

This copies the identity templates into `~/.mirror/your-name/identity/` and
substitutes your name into the template files automatically. The templates ship
as real, opinionated content — not placeholder fill-in forms.

### 1a. Migrate a legacy Portuguese-era database if needed

If you already have a legacy database such as `~/.espelho/memoria.db`, use the
explicit migration workflow before normal runtime use:

```bash
uv run python -m memory migrate-legacy validate \
  --source ~/.espelho/memoria.db \
  --target-home ~/.mirror/your-name \
  --report /tmp/mirror-migration-validate.json

uv run python -m memory migrate-legacy run \
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

### 2. What ships in your identity

After `memory init`, your identity home contains:

**Core identity** (used in every session):
- `self/soul.yaml` — worldview, operating principles, core role
- `ego/identity.yaml` — behavioral postures, how the mirror shows up
- `ego/behavior.yaml` — tone, intellectual method, universal constraints
- `user/identity.yaml` — your name, with room to deepen over time

**12 starter personas** — specialized lenses the mirror activates by context:

| Persona | Domain |
|---------|--------|
| `writer` | Writing, editing, voice, publishing |
| `thinker` | Ideas, decisions, conceptual clarity |
| `engineer` | Software, systems, debugging, architecture |
| `therapist` | Emotional processing, patterns, inner work |
| `strategist` | Business positioning, decisions, trade-offs |
| `coach` | Accountability, goals, habits, momentum |
| `researcher` | Inquiry, synthesis, evidence, analysis |
| `teacher` | Pedagogy, explanation, curriculum, mentoring |
| `doctor` | Health, symptoms, medical literacy |
| `financial` | Money, budgeting, investment, financial decisions |
| `designer` | Product design, UX, visual design, creative direction |
| `prompt-engineer` | Prompt design, AI system architecture, Mirror self-improvement |

**1 starter journey**: `personal-growth` — reflection, self-knowledge, values,
habits, meaning, and intentional change.

Your identity starts generic and sharpens through use. Refine any layer at your
own pace:

```bash
uv run python -m memory identity edit user identity
```

### 3. Populate the memory bank

Use the CLI as the runtime-neutral path:

```bash
uv run python -m memory seed
```

This loads identity from the active user home into the memory database. The mirror reads from the database at runtime; the user-home YAMLs are the seed source.

If you are already inside a runtime, you can also seed there:
- Pi: `/mm-seed`
- Gemini CLI: `/mm-seed` (via skill)
- Codex: `$mm-seed`
- Claude Code: `/mm:seed`

### 6. Start using

**Preferred: Pi**

Open Pi in this project and use commands such as:

```text
/mm-mirror
/mm-journeys
/mm-journey <slug>
/mm-consult ...
```

Pi is the preferred runtime because it makes Mirror Mind effectively multi-model.

**Gemini CLI**

```bash
gemini
```

Skills are discovered automatically from `.agents/skills/`. The mirror logs
conversations, injects identity context in Mirror Mode, and runs backups — all
without explicit invocation. Use the same `/mm-*` commands as Pi:

```text
/mm-mirror
/mm-journeys
/mm-journey <slug>
/mm-consult ...
```

**Codex**

```bash
# Use the wrapper script to run Codex with Mirror Mind
./scripts/codex-mirror.sh
```

Skills are discovered via the same symlinks in `.agents/skills/`. Mirror Mode
and Builder Mode are available via explicit `$mm-*` skill invocations:

```text
$mm-mirror
$mm-build <journey-slug>
$mm-journeys
$mm-consult ...
```

**Alternative: Claude Code**

```bash
claude
```

Then use commands such as:

```text
/mm:mirror
/mm:journeys
/mm:journey <slug>
/mm:consult ...
```

Claude Code is still fully supported, but it is now the secondary runtime rather than the primary one.

## Commands

| Pi / Gemini CLI | Codex | Claude Code | What it does |
|-----------------|-------|-------------|--------------|
| `/mm-mirror` | `$mm-mirror` | `/mm:mirror` | Mirror Mode — loads identity, persona, attachments and responds as you |
| `/mm-build` | `$mm-build` | `/mm:build` | Builder Mode — loads journey context and project docs |
| `/mm-consult` | `$mm-consult` | `/mm:consult` | Consult other LLMs via OpenRouter with mirror context |
| `/mm-journeys` | `$mm-journeys` | `/mm:journeys` | Quick list of all journeys |
| `/mm-journey` | `$mm-journey` | `/mm:journey` | Detailed journey status |
| `/mm-tasks` | `$mm-tasks` | `/mm:tasks` | Task management by journey |
| `/mm-week` | `$mm-week` | `/mm:week` | Weekly planning |
| `/mm-journal` | `$mm-journal` | `/mm:journal` | Record a personal journal entry |
| `/mm-memories` | `$mm-memories` | `/mm:memories` | List stored memories |
| `/mm-conversations` | `$mm-conversations` | `/mm:conversations` | Recent conversations list |
| `/mm-recall` | `$mm-recall` | `/mm:recall` | Load messages from a previous conversation into context |
| `/mm-identity` | `$mm-identity` | `/mm:identity` | Read and update identity in the database |
| `/mm-seed` | `$mm-seed` | `/mm:seed` | Seed identity from user home into the database |
| `/mm-mute` | `$mm-mute` | `/mm:mute` | Toggle conversation recording |
| `/mm-new` | `$mm-new` | `/mm:new` | Start a new conversation |
| `/mm-backup` | `$mm-backup` | `/mm:backup` | Backup the memory database |
| `/mm-help` | `$mm-help` | `/mm:help` | List available commands |

### Reference extensions

Some useful capabilities may ship in-repo temporarily as **reference
extensions** while the extension model matures. These are not part of Mirror
Mind core even if they are available as skills.

Current example:
- `examples/extensions/review-copy/` — the first external-skill reference tree,
  using `skill.yaml` plus `SKILL.md` with runtime names `ext:review-copy` and
  `ext-review-copy`
- `review-copy` is no longer shipped as a repo-local Claude or Pi skill; use
  the external install + runtime surfacing flow

## Architecture

### Psychic layers (Jungian)

- **Self/Soul** — Deep identity, purpose, frequency. The unchanging core.
- **Ego** — Operational identity and behavior. How the self manifests day-to-day.
- **Personas** — Specialized expressions of the ego in specific domains.
- **Shadow** (planned) — Detection of unconscious patterns.
- **Meta-Self** (planned) — System governance and meta-awareness.

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
- **Backups:** the runtime backup command zips the configured database into `DB_BACKUP_PATH`
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

### Extension quick start

Install an extension into your mirror home, then surface it at runtime:

```bash
# Install
uv run python -m memory extensions install \
  review-copy \
  --extensions-root examples/extensions \
  --mirror-home ~/.mirror/<user>

# Pi picks it up automatically on session start.
# Claude Code: expose it to a project explicitly.
# --target-root is required; there is no current-directory default.
uv run python -m memory extensions expose-claude \
  --mirror-home ~/.mirror/<user> \
  --target-root /path/to/project
```

- Pi command: `ext-review-copy`
- Claude Code command: `ext:review-copy`

The reference extension is at `examples/extensions/review-copy/`. For the full
extension CLI reference, see `REFERENCE.md`.

## Documentation

The full documentation lives under [`docs/`](docs/index.md):

- [Getting Started](docs/getting-started.md) — step-by-step onboarding for new users
- [Project Briefing](docs/project/briefing.md) — foundational architectural decisions
- [Decisions](docs/project/decisions.md) — decision log
- [Roadmap](docs/project/roadmap/index.md) — current and planned capability values
- [Development Guide](docs/process/development-guide.md) — how to work on this codebase
- [REFERENCE.md](REFERENCE.md) — full operational reference

## Stack

- **Python 3.10+** — memory and automation (managed with [uv](https://docs.astral.sh/uv/))
- **SQLite** — memory bank at `~/.mirror/<user>/memory.db`
- **OpenAI** — embeddings (text-embedding-3-small)
- **OpenRouter** — multi-LLM access (Gemini, GPT, Claude, etc.)
- **Claude Code** — supported alternative

## Principles

- **First person** — the AI speaks as you, not about you
- **One voice** — personas are lenses, not separate agents; the voice is always the ego's
- **Database as source of truth** — identity lives in the database after the first seed; YAML files are bootstrap material only

## License

MIT
