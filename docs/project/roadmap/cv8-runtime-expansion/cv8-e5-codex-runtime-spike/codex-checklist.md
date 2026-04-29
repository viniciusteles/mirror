[< CV8.E5 Codex Spike](index.md)

# Codex Implementation Checklist

Pre-work for the Codex spike. Derived from Gemini CLI lessons. The spike
answers the unknowns; these are the knowns from day one.

---

## What we already know (from Gemini CLI)

### Session ID
- Gemini CLI: stable UUID, available as `$GEMINI_SESSION_ID` env var in hooks
- Codex: unknown — does it inject a session ID env var? Does it have a hook stdin payload?
- **Checklist:** Confirm whether Codex exposes a session identifier. If not, design a deterministic fallback (e.g. hash of project path + timestamp, stored in a temp file for the session duration).

### Hook/lifecycle events
- Gemini CLI: `SessionStart`, `BeforeAgent`, `AfterAgent`, `SessionEnd` (best-effort)
- Codex: unknown — does it support lifecycle hooks at all? If yes, what are the event names and trigger conditions?
- **Checklist:** Map Codex's lifecycle events to the four Mirror Mind events. Identify which are missing and document as limitations.

### Hook communication protocol
- Gemini CLI and Claude Code: JSON on stdin → JSON on stdout; stderr for logs
- Codex: unknown — does it use stdin/stdout JSON? Shell exit codes?
- **Checklist:** Determine how hooks communicate. If JSON stdin/stdout: apply the stdout purity rule immediately (redirect all Python output to `/dev/null`). If different protocol: document and adapt.

### Context injection
- Gemini CLI: `BeforeAgent` `hookSpecificOutput.additionalContext`
- Claude Code: `UserPromptSubmit` outputs string injected as system note
- Codex: unknown — can it inject context before model response? What is the injection field?
- **Checklist:** Identify whether Codex supports pre-response context injection. If yes: target automatic per-turn injection (Gemini model). If no: document as L2 (no Mirror Mode auto-injection).

### Transcript access
- Claude Code: stable `transcript_path` in hook stdin at `SessionEnd`
- Gemini CLI: `transcript_path` in every hook stdin; used deferred extraction anyway
- Codex: unknown — does it write a session transcript? Is the path accessible?
- **Checklist:** Determine transcript availability. If available: use `session-end` with immediate extraction. If not: use `session-end-pi` with deferred extraction.

### Skill / command surface
- Gemini CLI: native SKILL.md at `.gemini/skills/` (same format as Pi)
- Claude Code: `SKILL.md` at `.claude/skills/`, invoked as `/mm:*`
- Codex: unknown — does it support slash commands? A custom instructions file? SKILL.md?
- **Checklist:** Identify the native command surface. If SKILL.md: symlink from `.pi/skills/`. If slash commands: adapt existing skills. If custom instructions only: document as L2 with limited command surface.

### Project-local configuration
- Gemini CLI: `.gemini/settings.json` for hooks; `.gemini/skills/` for skills
- Claude Code: `.claude/settings.json` for hooks; `.claude/skills/` for skills
- Codex: unknown — does it read a project-local config file?
- **Checklist:** Locate Codex's project config directory and file format before writing a single line of implementation.

---

## Known answers (no spike needed)

- **Interface label:** `codex` — pass `--interface codex` to `log-user` and `log-assistant`
- **Python changes:** none — `interface` is a free-text field
- **Smoke test isolation:** use `DB_PATH=/tmp/smoke-codex/memory.db` (not `MIRROR_HOME`)
- **Extraction model default:** `session-end-pi` unless transcript is confirmed available
- **Skill format default:** Pi-compatible SKILL.md symlinks if the runtime supports it
- **Stdout rule:** redirect all Python CLI output to `/dev/null` in shell hooks

---

## Spike output requirements

The E5 spike must answer every unknown above and produce:

1. A target parity level from the CV8 parity table (L0–L4)
2. A mapping of Codex lifecycle events to the runtime contract
3. A description of the context injection mechanism (or None)
4. A description of the command surface (or None)
5. A design for session ID handling (env var, stdin, or fallback)
6. An explicit list of limitations to document if parity < L4
7. An implementation plan for E6

---

## Parity level prediction

Based on Gemini CLI experience:

| Scenario | Likely parity |
|---|---|
| Codex has lifecycle hooks + context injection + skill surface | L4 |
| Codex has hooks + context injection, no native skill surface | L3 |
| Codex has hooks only, no injection | L2 |
| Codex has no hooks, only a custom instructions file | L1 (manual logging commands only) |
| Codex has nothing | L0 (CLI-assisted only) |

The spike confirms which scenario is real.
