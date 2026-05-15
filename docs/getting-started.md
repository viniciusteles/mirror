[< Docs](index.md)

# Getting Started

Mirror Mind is a local-first memory and identity framework for agentic AI runtimes. It gives each session access to the user's identity, voice, values, journeys, projects, and accumulated memory, so work can continue without starting from zero. The system is not a generic chatbot layer. It is Mirror Core: the architecture that lets Pi, Claude Code, Gemini CLI, and Codex operate with continuity, context, and coherence.

## Lineage and credits

Mirror Mind in this repository is a continuation of the original mirror work created by **Alisson Vale** in
[alissonvale/mirror-poc](https://github.com/alissonvale/mirror-poc/).
This version extends that foundation to support English-speaking users, Pi-based multi-model use, and stronger multi-user and multi-session runtime behavior.

The adoption of **Pi** was inspired by **Henrique Bastos** and his work in
[henriquebastos/mirror-mind](https://github.com/henriquebastos/mirror-mind),
which helped show the path toward a more model-flexible runtime.

Historically, **Claude Code was the initial harness** used in Alisson's original implementation. This continuation keeps Claude support, but Pi is now the preferred runtime because it enables a more multi-model setup.

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

- [Pi](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) — preferred runtime (multi-model)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) — fully supported runtime (`brew install gemini-cli`)
- [Codex](https://github.com/google-gemini/codex) — supported runtime
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — supported alternative runtime
- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — package manager

---

## 1. Clone and install

```bash
git clone https://github.com/viniciusteles/mirror.git
cd mirror
uv sync
```

`uv sync` creates a `.venv`, installs the exact dependency versions recorded in
`uv.lock`, and installs the `memory` package in editable mode. No manual venv
creation or `pip install` needed.

---

## 2. Configure environment variables

```bash
cp .env.example .env
```

The minimal `.env.example` covers what a new user actually needs:

```
MIRROR_USER=your-name              # resolves to ~/.mirror/<user>
# MIRROR_HOME=~/.mirror/your-name  # alternative: explicit path
OPENROUTER_API_KEY=sk-or-...       # embeddings, memory extraction, and /mm:consult
```

One of `MIRROR_USER` or `MIRROR_HOME` must be set in production. Everything
else (database path, export directories, backup directory, transcript
export, Pi sessions override, environment selection) is derived from that
root.

For the canonical list of every supported variable, its default, and its
role, see `.env.example.advanced` at the repo root or the Configuration
section of [REFERENCE.md](../REFERENCE.md#configuration).

---

## 3. Initialize your user home

Run:

```bash
uv run python -m memory init your-name
```

This copies the identity templates into `~/.mirror/your-name/identity/` and
substitutes your name into the template files automatically. **No manual editing
required** — the templates ship with real, opinionated content that works from
session one.

Your identity starts generic and sharpens through use. When something feels off
or too impersonal, refine it at your own pace:

```bash
uv run python -m memory identity edit user identity
```

### Legacy install note

If you already have a Portuguese-era database such as `~/.espelho/memoria.db`,
migrate it explicitly before normal use:

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

This workflow is safety-first:
- explicit source
- explicit target home
- no source mutation
- no merge into an existing target `memory.db`
- only clean Portuguese legacy DBs are supported

---

## 4. What ships in your identity

The templates are editorial products, not fill-in forms. After `memory init`,
your identity home contains:

**Core identity** (used in every session):
- `self/soul.yaml` — worldview, operating principles, core role
- `ego/identity.yaml` — behavioral postures, how the mirror shows up
- `ego/behavior.yaml` — tone, intellectual method, language rules
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

**1 starter journey** — `personal-growth`, a broadly useful arc for
reflection, self-knowledge, and intentional change.

All of this is ready to seed and use immediately. Edit, add, or remove anything
in your `~/.mirror/your-name/identity/` home as your needs evolve.

---

## 5. Seed the memory database

Use the CLI as the primary onboarding path:

```bash
uv run python -m memory seed
```

This loads YAML files from the active user home into the database. The mirror reads from the database at runtime; the user-home YAMLs are the seed source.

If you are already inside a runtime, the equivalent interactive entry points are:
- Pi: `/mm-seed`
- Gemini CLI: `/mm-seed` (via skill)
- Codex: `$mm-seed`
- Claude Code: `/mm:seed`

---

## 6. Start the mirror

### Preferred: Pi

Open Pi in this project and use the mirror through commands such as:

```text
/mm-mirror
/mm-journeys
/mm-journey <journey-slug>
/mm-consult ...
```

Pi is the preferred runtime because it lets Mirror Mind work across models more naturally.

### Gemini CLI

```bash
gemini
```

Skills are discovered automatically from `.agents/skills/`. The mirror logs
conversations in the background, injects identity context automatically in
Mirror Mode via the `BeforeAgent` hook, and runs backups on session end.
Use the same `/mm-*` commands as Pi:

```text
/mm-mirror
/mm-journeys
/mm-journey <journey-slug>
/mm-consult ...
```

### Codex

```bash
# Use the wrapper script to run Codex with Mirror Mind
./scripts/codex-mirror.sh
```

Skills are discovered automatically from the shared `.agents/skills/` surface.
Mirror Mode and Builder Mode are available via explicit `$mm-*` skill
invocations:

```text
$mm-mirror
$mm-build <journey-slug>
$mm-journeys
$mm-consult ...
```
The wrapper script handles session start, backfill, and end automatically.

### Alternative: Claude Code

```bash
claude
```

Then use commands such as:

```text
/mm:mirror
/mm:journeys
/mm:journey <journey-slug>
/mm:consult ...
```

Claude Code remains fully supported, but it is now the secondary runtime rather than the primary one.

---

## 7. Optional: install an extension

Mirror Mind core and extensions are separate.

- **Core skills** ship with the repo/runtime.
- **Extensions** are installed into your user-owned Mirror home.
- Runtimes consume the installed runtime surface, not the source extension tree directly.

### Extension locations

Source extension tree:

```text
~/.mirror/<user>/extensions/<id>/
```

Runtime materialization:

```text
~/.mirror/<user>/runtime/skills/pi/
~/.mirror/<user>/runtime/skills/claude/
```

### First example: `review-copy`

A reference extension example ships here:

```text
examples/extensions/review-copy/
```

Its runtime-visible commands are:
- Claude Code: `ext:review-copy`
- Pi: `ext-review-copy`

### Install it

```bash
uv run python -m memory extensions install \
  review-copy \
  --extensions-root examples/extensions \
  --mirror-home ~/.mirror/your-name
```

That does three things:
1. copies the source extension into `~/.mirror/your-name/extensions/review-copy/`
2. syncs the Pi runtime surface
3. syncs the Claude runtime surface

### Use it on Pi

Pi reads installed external skills from:

```text
~/.mirror/<user>/runtime/skills/pi/extensions.json
```

After install, Pi should discover `ext-review-copy` automatically from the runtime catalog.

### Use it on Claude Code

Claude needs an explicit project-local skill projection step. The
`--target-root` argument is required so generated extension overlays do not
accidentally land in whatever repository happens to be the current directory:

```bash
uv run python -m memory extensions expose-claude \
  --mirror-home ~/.mirror/your-name \
  --target-root /path/to/your/project
```

This creates a project-visible skill surface like:

```text
/path/to/your/project/.claude/skills/ext:review-copy/SKILL.md
/path/to/your/project/.claude/skills/extensions.external.json
```

After that, use the skill in Claude as:

```text
/ext:review-copy <file> <model1> [model2] ...
```

### Remove the Claude projection later

```bash
uv run python -m memory extensions clean-claude \
  --target-root /path/to/your/project
```

### Inspect and validate extensions

```bash
uv run python -m memory extensions validate --extensions-root examples/extensions
uv run python -m memory inspect extension review-copy --extensions-root examples/extensions
uv run python -m memory inspect runtime-catalog pi --mirror-home ~/.mirror/your-name
uv run python -m memory inspect runtime-catalog claude --mirror-home ~/.mirror/your-name
```

### Full smoke test

```bash
./scripts/smoke_external_review_copy.sh
```

---

## Verification

Confirm the onboarding flow worked end to end:

```bash
uv run python -m memory list personas --verbose
uv run python -m memory list journeys
uv run python -m memory detect-persona "I want help writing an article"
uv run python -m memory detect-persona "help me think through this idea"
uv run python -m memory detect-persona "debug this Python issue"
uv run python -m memory inspect persona writer
```

What to check:
- `list personas --verbose` shows your seeded personas and their `routing_keywords`
- `list journeys` shows your seeded journeys
- `detect-persona` returns sensible persona matches for a natural-language query
- `inspect persona ...` shows the persona metadata stored in the database, not just the YAML source

Optional extension verification:

```bash
uv run python -m memory inspect runtime-catalog pi --mirror-home ~/.mirror/your-name
uv run python -m memory inspect runtime-catalog claude --mirror-home ~/.mirror/your-name
```

Expected: the default personas (`writer`, `thinker`, `engineer`) or your customized personas appear with routing metadata, and `personal-growth` or your customized journeys appear in the journey list. If you installed `review-copy`, the runtime catalog output should also show `ext-review-copy` and `ext:review-copy`.

### Onboarding success checklist

You should now have all of the following:
- `~/.mirror/<user>/identity/` exists with your name already substituted in the templates
- `uv run python -m memory seed` completes without errors
- 12 personas appear in `uv run python -m memory list personas --verbose`
- `personal-growth` appears in `uv run python -m memory list journeys`
- persona routing responds sensibly in `uv run python -m memory detect-persona "..."`
- your runtime (Pi, Gemini CLI, Codex, or Claude Code) can use the seeded database

**Your first session will use a generic identity — that is expected and correct.**
The mirror sharpens through use. Deepen your profile over time with:
```bash
uv run python -m memory identity edit user identity
```

---

**See also:** [Briefing](project/briefing.md) (architecture decisions) · [REFERENCE.md](../REFERENCE.md) (full operational reference)
