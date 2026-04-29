[< Story](index.md)

# Plan — CV8.E1.S1 Inspect Codex Capabilities

## Purpose

Before implementing Codex support, inspect Codex's actual extension/runtime
surface and classify what level of Mirror Mind parity is possible.

The output of this story is evidence, not code.

---

## Current Mirror Runtime Contract

Mirror Mind runtimes integrate by satisfying these events:

| Event | Required behavior |
|-------|-------------------|
| Session start | run `uv run python -m memory conversation-logger session-start` |
| User prompt | log prompt with `conversation-logger log-user <session_id> <prompt> --interface <name>` |
| Assistant response | log assistant content explicitly or backfill from transcript |
| Session end | close session with `session-end` or `session-end-pi`, then backup |
| Mirror Mode | load context with `memory mirror load --context-only --query ... --session-id ...` |
| Command surface | expose core Mirror Mind commands in the runtime's native form |

Codex must be measured against this contract, not against an imagined ideal.

---

## Investigation Steps

### 1. Identify local Codex installation

Commands to run if Codex is expected to be installed:

```bash
which codex
codex --version
codex --help
```

Record:

- executable path
- version
- available subcommands/options relevant to config, commands, hooks, or logs

### 2. Inspect Codex documentation

Find official docs for:

- project instructions
- custom commands or slash commands
- hooks/lifecycle events
- transcript/log files
- configuration paths
- environment variables available to commands/hooks
- model context/system prompt customization

Record source links or local doc paths.

### 3. Inspect local configuration conventions

Look for existing Codex config locations, without mutating them:

```bash
find . -maxdepth 3 -iname '*codex*' -print
find ~ -maxdepth 3 -iname '*codex*' -print 2>/dev/null | head -100
```

Record likely project-local and user-local locations.

### 4. Probe project-local instructions

If Codex supports instruction files, create only temporary spike files or use a
throwaway directory. Confirm whether Codex reads:

- repository instruction files
- per-project config
- per-command prompt files

Record exact file names and precedence if known.

### 5. Probe command/customization surface

Determine whether Codex can expose a Mirror command surface equivalent to:

- `mm-mirror`
- `mm-build`
- `mm-journey`
- `mm-tasks`
- `mm-memories`
- `mm-consult`
- etc.

Record whether commands can:

- run shell commands
- receive user arguments
- include prompt text
- read files
- return generated context to the model

### 6. Probe lifecycle hooks

Determine whether Codex can trigger commands on:

- session start
- user prompt before model response
- assistant response after model response
- session shutdown

For each event, record:

- whether it exists
- payload shape
- whether prompt/response text is available
- whether a session id is available
- whether shell commands can be run

### 7. Probe transcript/log availability

Determine whether Codex writes transcripts or logs that can be backfilled.

Record:

- path
- format
- whether user and assistant messages are included
- whether session id can be derived from the path

### 8. Classify context injection

Classify Codex's Mirror Mode potential:

| Classification | Meaning |
|----------------|---------|
| pre-response | Codex can inject identity context before the model responds |
| command-only | Codex can load context only through explicit user commands |
| unavailable | Codex cannot reliably put Mirror context in front of the model |

This classification drives the Codex parity level.

---

## Evidence Log

Fill this during the spike.

### Installation

- Codex installed: yes
- Path: `/opt/homebrew/bin/codex`
- Binary target: `/opt/homebrew/Caskroom/codex/0.125.0/codex-aarch64-apple-darwin`
- Version: `codex-cli 0.125.0`
- Top-level commands observed from `codex --help`: `exec`, `review`, `login`,
  `logout`, `mcp`, `plugin`, `mcp-server`, `app-server`, `app`, `completion`,
  `sandbox`, `debug`, `apply`, `resume`, `fork`, `cloud`, `exec-server`,
  `features`, `help`.

### Docs / Sources

- Local help inspected: `codex --help`, `codex exec --help`, `codex plugin --help`,
  `codex plugin marketplace --help`, `codex debug --help`,
  `codex debug prompt-input --help`, `codex mcp --help`.
- Local Codex home inspected: `~/.codex/`.
- Skill creation docs inspected:
  - `~/.codex/skills/.system/skill-creator/SKILL.md`
  - `~/.codex/skills/.system/skill-creator/references/openai_yaml.md`
- Plugin creation docs inspected:
  - `~/.codex/skills/.system/plugin-creator/SKILL.md`
  - `~/.codex/skills/.system/plugin-creator/references/plugin-json-spec.md`
- Official web docs not inspected yet in this story.

### Project-local config

- User config exists at `~/.codex/config.toml`.
- User instructions exist at `~/.codex/AGENTS.md`.
- `codex debug prompt-input "probe prompt"` shows that project instructions are
  loaded as `# AGENTS.md instructions for /Users/vinicius/dev/workspace/mirror`.
- `~/.codex/config.toml` records trusted projects under `[projects."<path>"]`.
- Plugin scaffolding docs describe repo-local marketplace path
  `<repo-root>/.agents/plugins/marketplace.json` and repo-local plugin source
  `./plugins/<plugin-name>`.
- Plugin manifest path convention: `<plugin-root>/.codex-plugin/plugin.json`.

### Command surface

- Codex supports skills under `~/.codex/skills/<skill-name>/SKILL.md`.
- Skill discovery is visible in `codex debug prompt-input`; available skills are
  injected as name + description + file path.
- Skills are instruction bundles, not executable slash-command handlers. They can
  include `scripts/`, `references/`, and `assets/`, and Codex may run scripts as
  normal shell/tool actions while following the skill.
- Plugins can contribute skills via a manifest with `"skills": "./skills/"`.
- Plugin docs also mention optional `hooks`, `mcpServers`, and `apps` manifest
  fields, but the hook payload/schema has not been found yet.
- Native CLI command `codex exec` can run non-interactively and supports `--json`
  event output plus `--output-last-message <FILE>`.

### Lifecycle hooks

- Not confirmed yet.
- Plugin manifest supports a top-level `hooks` path in the sample spec, but the
  inspected local docs only identify the field, not hook event names, payloads,
  or execution semantics.
- No evidence yet of built-in lifecycle hooks equivalent to Claude Code hooks or
  Pi extension events.

### Session id

- Codex has stable thread ids in `~/.codex/session_index.jsonl` and
  `~/.codex/state_5.sqlite`.
- `state_5.sqlite` table `threads` has `id TEXT PRIMARY KEY` and
  `rollout_path TEXT NOT NULL`.
- Recent thread ids are UUID-like values such as
  `019dd3be-9122-7900-9984-feec57df257a`.
- This can likely serve as the Mirror runtime `session_id` for backfill-based
  integration if we can reliably discover the active thread id/path.

### Prompt/assistant capture

- Historical prompt/assistant data is available in rollout JSONL files under
  `~/.codex/sessions/YYYY/MM/DD/rollout-...<thread-id>.jsonl`.
- Rollout entries include `response_item` payloads with `role: user`,
  `role: assistant`, and developer/system context, plus `event_msg` entries like
  `user_message` and `task_started`.
- `codex exec --json` advertises JSONL event output for non-interactive runs;
  not yet tested with a real model call in this spike.
- Interactive per-turn hook capture is not confirmed yet.

### Transcript/log availability

- Session index exists: `~/.codex/session_index.jsonl`.
- State database exists: `~/.codex/state_5.sqlite`.
- Logs database exists: `~/.codex/logs_2.sqlite`.
- `state_5.sqlite` table `threads` maps `id` to `rollout_path`, `cwd`, `source`,
  `title`, model metadata, and timestamps.
- Rollout JSONL transcript files exist under `~/.codex/sessions/...` and include
  structured user/assistant messages.
- This suggests a Claude-style transcript backfill may be more realistic than a
  Pi-style live event logger unless Codex plugin hooks prove usable.

### Context injection

- `codex debug prompt-input` proves Codex composes model-visible context from
  developer instructions, skills/plugins, AGENTS.md, environment context, and the
  user prompt.
- Project `AGENTS.md` is a confirmed context-injection mechanism at session/turn
  composition time, but it is static file content, not dynamic per-turn Mirror
  context.
- Codex skills can be discovered and loaded via SKILL.md, but current evidence
  indicates they are procedural instructions rather than automatic pre-response
  dynamic context injection.
- Dynamic pre-response Mirror Mode injection is not confirmed yet.

---

## Preliminary Parity Assessment

Use the CV8 parity levels:

| Level | Name | Meaning |
|-------|------|---------|
| L0 | CLI-assisted | Can call `uv run python -m memory ...`, but no automatic logging/context injection |
| L1 | Logged runtime | User and assistant turns are persisted; sessions close cleanly |
| L2 | Command surface | Core Mirror commands are available through native command mechanism |
| L3 | Mirror Mode runtime | Identity/context can be injected before model response |
| L4 | Full parity | Logging, command surface, Mirror Mode, Builder Mode, external skills/equivalent, smoke validation |

Initial Codex target parity: **provisionally L2, with possible L1/L3 depending on hooks**

Rationale:

- L2 looks realistic because Codex has a native skill/plugin surface. Mirror Mind
  can likely expose procedural skills that call `uv run python -m memory ...`.
- L1 looks realistic through transcript backfill because Codex stores thread ids
  and rollout JSONL transcripts, but active-session discovery still needs proof.
- L3 is not proven. Static `AGENTS.md` and skills inject instructions, but we do
  not yet have evidence of dynamic pre-response context injection on every turn.
- L4 requires L3 plus smoke validation and external-skill parity; not justified
  by current evidence.

---

## Risks

- Codex may not expose lifecycle hooks
- Codex may expose commands but not pre-response context injection
- Codex may not provide stable session ids
- Codex may store transcripts in an undocumented format
- Codex customization may be user-global rather than project-local
- runtime limitations may force lower parity than Pi or Claude Code

---

## Exit Criteria

This story can close when we can write CV8.E1.S2 with concrete lifecycle mapping
instead of speculation.
