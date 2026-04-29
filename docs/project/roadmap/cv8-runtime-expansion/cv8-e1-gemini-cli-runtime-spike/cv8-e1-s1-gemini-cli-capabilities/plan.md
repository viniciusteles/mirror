[< Story](index.md)

# Plan — CV8.E1.S1 Inspect Gemini CLI Capabilities

## Purpose

Before implementing Gemini CLI support, inspect Gemini CLI's actual extension and
runtime surface and classify what level of Mirror Mind parity is possible.

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

Gemini CLI must be measured against this contract, not against an imagined ideal.

---

## Investigation Steps

### 1. Identify local Gemini CLI installation

Commands run:

```bash
which gemini
gemini --version
gemini --help
```

Record:

- executable path
- version
- available subcommands/options relevant to config, commands, hooks, skills,
  extensions, logs, and session handling

### 2. Inspect Gemini CLI documentation

Local bundled docs inspected:

- hooks overview
- hooks reference
- writing hooks
- extensions guide
- extensions reference
- skills guide
- creating skills guide
- custom commands guide
- GEMINI.md guide

### 3. Inspect local configuration conventions

Look for Gemini CLI config locations, without mutating them:

```bash
ls -la ~/.gemini
find ~/.gemini -maxdepth 4 -type f
find . -maxdepth 4 \( -iname '*gemini*' -o -name 'GEMINI.md' \) -print
```

Record likely project-local and user-local locations.

### 4. Probe project-local instructions

Confirm Gemini CLI context mechanisms:

- `GEMINI.md` hierarchy
- configurable context file names via `settings.json`
- extension-level `GEMINI.md`
- JIT context loading

### 5. Probe command/customization surface

Determine whether Gemini CLI can expose a Mirror command surface equivalent to:

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
- inject command output into prompts
- read files
- be distributed through extensions

### 6. Probe lifecycle hooks

Determine whether Gemini CLI can trigger commands on:

- session start
- before agent / user prompt
- before model
- after model
- after agent / assistant response
- session end

For each event, record:

- whether it exists
- payload shape
- whether prompt/response text is available
- whether a session id is available
- whether shell commands can be run

### 7. Probe transcript/log availability

Determine whether Gemini CLI writes transcripts or histories that can be
backfilled.

Record:

- path
- format
- whether user and assistant messages are included
- whether session id can be derived from the path

### 8. Classify context injection

Classify Gemini CLI's Mirror Mode potential:

| Classification | Meaning |
|----------------|---------|
| pre-response | Gemini CLI can inject identity context before the model responds |
| command-only | Gemini CLI can load context only through explicit user commands |
| unavailable | Gemini CLI cannot reliably put Mirror context in front of the model |

This classification drives the Gemini CLI parity level.

---

## Evidence Log

### Installation

- Gemini CLI installed: yes
- Path: `/opt/homebrew/bin/gemini`
- Version: `0.38.2`
- Top-level commands observed from `gemini --help`: `mcp`, `extensions`,
  `skills`, `hooks`, and default interactive query mode.
- Relevant top-level options observed: `--prompt` for non-interactive headless
  mode, `--prompt-interactive`, `--resume`, `--list-sessions`,
  `--output-format text|json|stream-json`, `--extensions`, `--list-extensions`,
  `--approval-mode`, `--include-directories`, and `--acp`.

### Docs / Sources

- Local help inspected: `gemini --help`, `gemini extensions --help`,
  `gemini skills --help`, `gemini hooks --help`, `gemini hooks migrate --help`,
  `gemini mcp --help`, `gemini --list-sessions`.
- Local Gemini home inspected: `~/.gemini/`.
- Bundled docs inspected:
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/hooks/index.md`
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/hooks/reference.md`
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/hooks/writing-hooks.md`
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/extensions/writing-extensions.md`
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/extensions/reference.md`
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/cli/skills.md`
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/cli/creating-skills.md`
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/cli/custom-commands.md`
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/docs/cli/gemini-md.md`
- Built-in `skill-creator` inspected:
  - `/opt/homebrew/Cellar/gemini-cli/0.38.2/libexec/lib/node_modules/@google/gemini-cli/bundle/builtin/skill-creator/SKILL.md`

### Project-local config

- User config exists at `~/.gemini/settings.json`.
- Project registry exists at `~/.gemini/projects.json` and includes
  `/Users/vinicius/dev/workspace/mirror`.
- Trusted folders exist at `~/.gemini/trustedFolders.json`.
- Project history root exists at `~/.gemini/history/mirror/`.
- Gemini CLI supports project settings in `.gemini/settings.json`.
- Gemini CLI supports project-local commands in `<project>/.gemini/commands/`.
- Gemini CLI supports workspace skills in `.gemini/skills/` or `.agents/skills/`.
- Gemini CLI supports project/context files named `GEMINI.md`, configurable via
  `settings.json` (`context.fileName`).

### Command surface

- Gemini CLI has native custom commands via TOML files:
  - user commands: `~/.gemini/commands/`
  - project commands: `<project>/.gemini/commands/`
- Command names are derived from paths: `commands/test.toml` -> `/test`,
  `commands/git/commit.toml` -> `/git:commit`.
- Commands can receive arguments via `{{args}}`.
- Commands can execute shell injections with `!{...}` and inject output into the
  prompt after user confirmation.
- Commands can inject file content with `@{...}`.
- Gemini CLI supports skills:
  - workspace: `.gemini/skills/` or `.agents/skills/`
  - user: `~/.gemini/skills/` or `~/.agents/skills/`
  - extension-bundled skills under `skills/`
- Gemini CLI supports extensions with `commands/`, `skills/`, `hooks/`, MCP
  servers, context files, policies, themes, and sub-agents.

### Lifecycle hooks

- Gemini CLI has first-class hooks configured through `settings.json` and
  extension `hooks/hooks.json`.
- Confirmed hook events from docs:
  - `SessionStart`
  - `SessionEnd`
  - `BeforeAgent`
  - `AfterAgent`
  - `BeforeModel`
  - `AfterModel`
  - `BeforeToolSelection`
  - `BeforeTool`
  - `AfterTool`
  - `PreCompress`
  - `Notification`
- Hooks communicate via JSON on stdin/stdout and logs on stderr.
- Hook commands are shell commands with configurable timeout.
- Base hook input includes:
  - `session_id`
  - `transcript_path`
  - `cwd`
  - `hook_event_name`
  - `timestamp`
- Hook environment includes:
  - `GEMINI_PROJECT_DIR`
  - `GEMINI_SESSION_ID`
  - `GEMINI_CWD`
  - `CLAUDE_PROJECT_DIR` compatibility alias

### Session id

- Gemini CLI exposes stable session ids.
- `gemini --list-sessions` in this project returned two sessions, including ids:
  - `1aa2516c-ad88-463f-8966-30d3c8d17e1b`
  - `44b4d301-c413-47a1-a9e6-419e1f03cd78`
- Hook base input includes `session_id`.
- Hook environment includes `GEMINI_SESSION_ID`.
- This directly satisfies Mirror Mind's session id requirement.

### Prompt/assistant capture

- `BeforeAgent` input includes `prompt`, the original text submitted by the user.
- `AfterAgent` input includes `prompt` and `prompt_response`, the final text
  generated by the agent.
- `BeforeModel` input includes `llm_request` with model, messages, config, and
  tool config.
- `AfterModel` input includes `llm_request` and `llm_response`; it fires for
  every streaming chunk.
- `AfterModel` can be used for low-level model logging, but `AfterAgent` looks
  better for Mirror Mind's assistant-turn logging because it contains the final
  response text once per turn.

### Transcript/log availability

- Hook base input includes `transcript_path`, an absolute path to the session
  transcript JSON.
- Gemini CLI also keeps project history under `~/.gemini/history/<project>/`.
- Since hooks already provide both prompt/response text and transcript path,
  Mirror Mind can choose either Pi-style explicit turn logging or Claude-style
  transcript backfill.
- Explicit hook logging via `BeforeAgent` + `AfterAgent` appears simpler and
  more direct than transcript backfill.

### Context injection

- Gemini CLI has confirmed dynamic pre-response context injection.
- `SessionStart` can return `hookSpecificOutput.additionalContext`, injected as
  the first turn in interactive history or prepended to the prompt in
  non-interactive mode.
- `BeforeAgent` can return `hookSpecificOutput.additionalContext`, appended to
  the prompt for the current turn only.
- This directly supports Mirror Mode identity/context injection before the model
  responds.
- Gemini CLI also supports static context through `GEMINI.md`, extension
  `contextFileName`, and hierarchical/JIT context loading.

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

Initial Gemini CLI target parity: **L4 is plausible**

Rationale:

- L1 is directly supported through `BeforeAgent`, `AfterAgent`, `SessionStart`,
  `SessionEnd`, stable `session_id`, and `transcript_path`.
- L2 is directly supported through custom commands, skills, and extensions.
- L3 is directly supported through `BeforeAgent` additional context injection.
- L4 is plausible because Gemini CLI supports extensions bundling commands,
  skills, hooks, MCP servers, and static context. Final L4 classification still
  requires implementation and isolated smoke validation.

---

## Risks

- `SessionEnd` is best-effort and the CLI does not wait for it to complete;
  extraction/backup must be robust to missed or interrupted shutdown hooks.
- `AfterModel` fires for every streaming chunk; using it naively could duplicate
  assistant messages. Prefer `AfterAgent` for final assistant response logging.
- Dynamic context injection through `BeforeAgent` appends to the prompt, not
  necessarily to a system/developer channel. Prompt placement must be evaluated
  for Mirror Mode quality.
- Hook trust/fingerprinting may require user approval for project-level hooks.
- Custom commands that run shell injections require confirmation unless policy
  allows them.
- Gemini CLI support may end up stronger than Codex support. The CV8 order was
  later inverted so Gemini CLI shipped first and Codex second.

---

## Exit Criteria

This story can close when we can write CV8.E2 with concrete lifecycle mapping
instead of speculation.
