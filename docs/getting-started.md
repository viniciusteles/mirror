[< Docs](index.md)

# Getting Started

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Python 3.10+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — package manager
- An OpenAI API key (embeddings)
- An OpenRouter API key (LLM extraction and multi-LLM consult)

---

## 1. Clone and install

```bash
git clone https://github.com/viniciusteles/mirror-poc.git
cd mirror-poc
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
OPENAI_API_KEY=sk-...              # embeddings
OPENROUTER_API_KEY=sk-or-...       # memory extraction and /mm:consult
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
python -m memory init your-name
```

This copies the repository templates into:

```text
~/.mirror/your-name/identity/
```

### Legacy install note

If you already have a Portuguese-era database such as `~/.espelho/memoria.db`,
migrate it explicitly before normal use:

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

This workflow is safety-first:
- explicit source
- explicit target home
- no source mutation
- no merge into an existing target `memory.db`
- only clean Portuguese legacy DBs are supported

## 4. Fill in your identity

Mirror Mind seeds from the active user home. Edit the YAML files under:

```text
~/.mirror/your-name/identity/
```

The minimum required structure is:

| File | What it holds |
|------|---------------|
| `~/.mirror/your-name/identity/self/soul.yaml` | Who you are at the deepest level — purpose, values, worldview |
| `~/.mirror/your-name/identity/ego/identity.yaml` | Operational identity — what you do, how you present |
| `~/.mirror/your-name/identity/ego/behavior.yaml` | Tone and style — how the mirror speaks |
| `~/.mirror/your-name/identity/user/identity.yaml` | Your profile: name, role, background |
| `~/.mirror/your-name/identity/organization/identity.yaml` | Your company or project (optional) |

Optional sections live under the same `identity/` root:
- `organization/`
- `personas/`
- `journeys/`

Repository templates now live under `templates/identity/`. Live identity belongs under `~/.mirror/<user>/identity/`; normal seed input does not come from the repository.

---

## 5. Seed the memory database

```bash
claude
```

Inside Claude Code:

```
/mm:seed
```

This loads YAML files from the active user home into the database. The mirror reads from the database at runtime; the user-home YAMLs are the seed source.

---

## 6. Configure persona routing

Open `CLAUDE.md` and map your personas to domains:

```markdown
**Routing by domain:**
- Writing/blog/articles → `writer`
- Therapy/existential → `therapist`
- Finance/budget → `treasurer`
```

---

## 7. Start the mirror

```bash
claude
```

Just talk. The ego routes to the right persona based on context. For explicit Mirror Mode, use `/mm:mirror`. For Builder Mode on a specific journey, use `/mm:build <journey-slug>`.

---

## 8. Optional: install an extension

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
python -m memory extensions install \
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

Claude needs an explicit project-local skill projection step:

```bash
python -m memory extensions expose-claude \
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
python -m memory extensions clean-claude \
  --target-root /path/to/your/project
```

### Inspect and validate extensions

```bash
python -m memory extensions validate --extensions-root examples/extensions
python -m memory inspect extension review-copy --extensions-root examples/extensions
python -m memory inspect runtime-catalog pi --mirror-home ~/.mirror/your-name
python -m memory inspect runtime-catalog claude --mirror-home ~/.mirror/your-name
```

### Full smoke test

```bash
./scripts/smoke_external_review_copy.sh
```

---

## Verification

Confirm the setup is working:

```bash
uv run python -m memory list journeys   # shows seeded journeys
uv run python -m memory list personas   # shows seeded personas
```

Optional extension verification:

```bash
python -m memory inspect runtime-catalog pi --mirror-home ~/.mirror/your-name
python -m memory inspect runtime-catalog claude --mirror-home ~/.mirror/your-name
```

Expected: your journeys and personas appear in the output. If you installed
`review-copy`, the runtime catalog output should also show `ext-review-copy`
and `ext:review-copy`.

---

**See also:** [Briefing](project/briefing.md) (architecture decisions) · [REFERENCE.md](../REFERENCE.md) (full operational reference)
