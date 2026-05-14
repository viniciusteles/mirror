[< CV9.E2 Stabilization & Robustness](../index.md)

# CV9.E2.S2 — External Extension Runtime Surface Parity

**Status:** Planned  
**Epic:** CV9.E2 Stabilization & Robustness  
**Task:** `92c028c7` — Add external extension skill projection for Gemini CLI and Codex

---

## User-Visible Outcome

An installed external extension should be discoverable as a normal skill in every
supported runtime whose skill system can support it. Pi and Claude Code already
have first-class external-skill visibility; Gemini CLI and Codex should not be
second-class citizens that require the user to remember raw `python -m memory
ext ...` commands.

For Gemini CLI and Codex, the likely user-visible result is an explicit
projection command that writes installed external skills into the shared
project-local `.agents/skills/` surface, analogous to Claude's
`expose-claude --target-root <project>` flow.

---

## Problem

The extension core is runtime-neutral: installed `command-skill` extensions can
be invoked through:

```bash
uv run python -m memory ext <extension-id> <subcommand> ...
```

That works from any shell-capable runtime. Mirror Mode context providers are
also core-side and can be collected during prompt assembly independently of the
frontend.

The gap is **runtime skill discovery**.

Current state:

| Runtime | External extension skill visibility | Status |
|---|---:|---|
| Pi | Reads `~/.mirror/<user>/runtime/skills/pi/extensions.json` and contributes installed `SKILL.md` paths | First-class |
| Claude Code | Uses explicit `expose-claude --target-root <project>` projection into `.claude/skills/` | First-class, manual projection |
| Gemini CLI | Uses the shared `.agents/skills/` surface for core skills | Missing external projection |
| Codex | Uses the shared `.agents/skills/` surface for core skills | Missing external projection |

So extension **commands** work everywhere, but extension **skill UX** does not.
That creates an inconsistent runtime contract: a user can install
`google-workspace`, see it naturally in Pi, expose it explicitly to Claude, but
not get an equivalent first-class skill surface in Gemini CLI or Codex.

---

## Proposed Direction

Add a shared `agents` external-skill runtime surface because Gemini CLI and Codex
already share `.agents/skills/` for core Mirror skills.

Likely installed/runtime shape:

```text
~/.mirror/<user>/runtime/skills/agents/ext-google-workspace/SKILL.md
~/.mirror/<user>/runtime/skills/agents/extensions.json
```

Likely project projection command:

```bash
uv run python -m memory extensions expose-agents \
  --mirror-home ~/.mirror/<user> \
  --target-root /path/to/project
```

and cleanup:

```bash
uv run python -m memory extensions clean-agents \
  --target-root /path/to/project
```

The projection should follow the safety rule learned from Claude: explicit
`--target-root` required, no current-working-directory default.

---

## Design Notes

- Prefer one shared `agents` runtime over separate `gemini` and `codex` runtimes
  unless their external-skill formats diverge. The discovery mechanism is shared,
  so the projection should be shared.
- Keep extension source under `~/.mirror/<user>/extensions/<id>/` and runtime
  materialization under `~/.mirror/<user>/runtime/skills/<runtime>/`.
- Project-local `.agents/skills/ext-*/` entries should be treated as generated
  overlays, not framework source.
- The projection must not disturb existing core `.agents/skills/mm-*` symlinks.
- The command names need an explicit decision. Since Gemini CLI invokes skills
  with `/...` and Codex with `$...`, but both read `.agents/skills/`, the skill
  directory and manifest naming should be tested in both runtimes before the
  contract is finalized.

---

## Scope

In scope:

- Add extension runtime materialization for a shared `agents` target if the
  manifest supports it, or derive it safely from existing runtime metadata if
  that proves cleaner.
- Add explicit project projection and cleanup commands for `.agents/skills/`.
- Add regression tests proving projection requires `--target-root`.
- Add tests proving existing core `.agents/skills/mm-*` entries are not pruned or
  overwritten.
- Update README, Getting Started, REFERENCE, and runtime-interface docs.

Out of scope:

- Changing the extension loading API.
- Marketplace/remote extension installation.
- Runtime hook lifecycle changes for Gemini CLI or Codex.
- Automatic per-turn extension discovery beyond existing Mirror Mode context
  provider behavior.

---

## Done Condition

- Installed external extensions can be surfaced as project-local skills for both
  Gemini CLI and Codex through the shared `.agents/skills/` surface.
- The projection and cleanup commands require explicit `--target-root`.
- Generated `.agents/skills/` external overlays are documented and gitignored as
  needed without hiding core `mm-*` symlinks.
- Existing Pi and Claude external-skill behavior continues to pass regression
  tests.
- Documentation clearly explains the difference between extension core command
  support and runtime skill discovery.

---

## See also

- [CV9.E2 Stabilization & Robustness](../index.md)
- [Runtime Interface Contract](../../../../product/specs/runtime-interface/index.md)
- [Extension Architecture](../../../../product/extensions/architecture.md)
