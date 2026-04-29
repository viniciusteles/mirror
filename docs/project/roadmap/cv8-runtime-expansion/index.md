[< Roadmap](../index.md)

# CV8 — Runtime Expansion: Gemini CLI and Codex

**Status:** In progress
**Goal:** Make Mirror Mind run as a first-class mirror runtime on top of Gemini CLI first and Codex second, without duplicating business logic outside the shared Python core.

---

## What This Is

CV1 proved that Mirror Mind could move beyond Claude Code by adding Pi as a
second interface over the same `src/memory/` core. CV2–CV6 then hardened that
runtime model: portable CLI boundaries, skill parity, user homes, multisession
safety, and external skills. CV8 takes the next architectural step: prove that
Mirror Mind can attach to more coding-agent runtimes without becoming a set of
runtime-specific forks.

The target runtimes are ordered deliberately:

1. **Gemini CLI** — first new runtime after Claude Code and Pi
2. **Codex** — second, implemented only after Gemini CLI teaches us what needs
   to be generalized

The original plan had Codex first. The order was inverted because Gemini CLI
(0.38.2) was already installed, its hook model was immediately inspectable, and
the spike revealed full L4 parity is achievable with shell hooks — a model
closer to Claude Code than to Pi. Gemini CLI produces the clearest first test
of the runtime adapter contract. Codex comes second after Gemini CLI lessons are
folded back into the adapter hardening epic.

The work is not to rewrite Mirror Mind for either tool. The work is to add two
thin runtime adapters that satisfy the existing runtime contract:

- session start
- user prompt logging
- assistant response logging or transcript backfill
- session end
- backup
- Mirror Mode identity/context loading
- command/skill surface for core operations

If a runtime cannot expose some of these events, CV8 must document the limitation
honestly rather than pretending parity exists.

---

## Product Outcome

A user can open Gemini CLI or Codex in a Mirror Mind project and use the mirror
with continuity:

- conversations are persisted under the active `~/.mirror/<user>/memory.db`
- user and assistant turns are logged with `interface='gemini_cli'` or
  `interface='codex'`
- Mirror Mode can load identity, persona, journey, memories, and attachments
- Builder Mode can load a journey and project docs
- existing memory, task, journey, identity, backup, and consult commands remain
  available through the runtime's native command mechanism where possible
- runtime limitations are explicit in docs and smoke tests

---

## Non-Goals

- No new memory implementation per runtime
- No Gemini CLI-specific or Codex-specific database schema beyond interface labels,
  unless the runtime genuinely requires metadata we cannot represent today
- No hosted service or daemon as part of CV8
- No rewrite of existing Claude Code or Pi behavior unless Gemini CLI/Codex work
  exposes a shared runtime contract bug
- No fake parity: if a runtime lacks hooks or context injection, the integration
  is documented as partial

---

## Runtime Parity Levels

CV8 uses explicit parity levels so the implementation does not blur real
capability with aspiration.

| Level | Name | Meaning |
|-------|------|---------|
| L0 | CLI-assisted | The runtime can call `uv run python -m memory ...`, but has no automatic logging or context injection |
| L1 | Logged runtime | User and assistant turns are persisted, sessions close cleanly, backups run |
| L2 | Command surface | Core Mirror Mind commands are available through the runtime's native command mechanism |
| L3 | Mirror Mode runtime | Identity/context can be injected before the model responds, with session-scoped state |
| L4 | Full parity | Runtime supports logging, command surface, Mirror Mode, Builder Mode, external skills or equivalent discoverability, and isolated smoke validation |

**Gemini CLI target: L4.** The hook model (shell scripts via `.gemini/settings.json`),
per-turn context injection (`BeforeAgent` → `additionalContext`), stable session ID
(`$GEMINI_SESSION_ID`), transcript file (`transcript_path` in every hook stdin), and
native SKILL.md discovery (`.gemini/skills/`) together satisfy every parity requirement.
The only honest limitation: `SessionEnd` is best-effort. Extraction defers to next
`SessionStart` — the same model used by Pi, already battle-tested.

**Codex target:** TBD after CV8.E1.

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|----------------------|--------|
| [CV8.E1](cv8-e1-gemini-cli-runtime-spike/index.md) | Gemini CLI Runtime Spike | Gemini CLI capabilities fully mapped; target parity L4 confirmed | Done |
| [CV8.E2](cv8-e2-gemini-cli-runtime-implementation/index.md) | Gemini CLI Runtime Implementation | Gemini CLI can run Mirror Mind through shell hooks over the Python core | Done |
| [CV8.E3](cv8-e3-gemini-cli-operational-validation/index.md) | Gemini CLI Operational Validation & Docs | Gemini CLI integration is smoke-tested, documented, and safe against production DB leakage | Done |
| [CV8.E4](cv8-e4-runtime-adapter-hardening/index.md) | Runtime Adapter Hardening | Lessons from Gemini CLI are folded into reusable runtime guidance before Codex work starts | Done |
| [CV8.E5](cv8-e5-codex-runtime-spike/index.md) | Codex Runtime Spike | We know exactly what Codex exposes and what parity level is realistic | Draft |
| [CV8.E6](cv8-e6-codex-runtime-implementation/index.md) | Codex Runtime Implementation | Codex can run Mirror Mind through a thin adapter over the Python core | Draft |
| [CV8.E7](cv8-e7-codex-operational-validation/index.md) | Codex Operational Validation & Docs | Codex integration is smoke-tested, documented, and safe against production DB leakage | Draft |

---

## Done Condition

CV8 is done when:

- Gemini CLI runtime capabilities are investigated and mapped against
  `docs/project/runtime-interface.md`
- Gemini CLI has the highest honest parity level its hook model supports (L4)
- Gemini CLI conversations write `interface='gemini_cli'` and are session-safe
- Gemini CLI Mirror Mode works via `BeforeAgent` `additionalContext` injection
- Gemini CLI has an isolated smoke test that proves no production database is touched
- Gemini CLI setup and usage are documented in README, Getting Started, REFERENCE,
  Runtime Interface Contract, and runtime-specific skill/command docs
- Gemini CLI lessons are folded back into the runtime contract before Codex work begins
- Codex runtime capabilities are investigated and mapped against the same contract
- Codex has the highest honest parity level its extension/hook model supports
- Codex conversations write `interface='codex'` and are session-safe
- Codex Mirror Mode works if the runtime supports pre-response context injection;
  otherwise the limitation is documented as lower parity
- Codex has an isolated smoke test that proves no production database is touched
- all runtime-facing docs clearly distinguish Claude Code, Pi, Gemini CLI, and Codex
  support levels

---

## Sequencing

```text
E1 Gemini CLI spike (done)
  └── E2 Gemini CLI implementation
        └── E3 Gemini CLI validation + docs
              └── E4 runtime adapter hardening
                    └── E5 Codex spike
                          └── E6 Codex implementation
                                └── E7 Codex validation + docs
```

Gemini CLI comes first because it was already installed, the spike produced
immediate and complete findings, and L4 parity is achievable with a familiar
shell-hook model. Codex comes second and benefits from the adapter hardening that
Gemini CLI forces.

---

## Open Questions (Codex — to be answered in E5)

- Does Codex expose lifecycle hooks equivalent to session start, user prompt,
  assistant response, and session end?
- Does Codex expose a stable session id?
- Can Codex inject context before the model response, or only through explicit
  commands?
- Does Codex expose transcript paths, per-turn events, or neither?
- What local project file structure does Codex use for custom commands, skills,
  or hooks?

---

## See also

- [Runtime Interface Contract](../../runtime-interface.md)
- [CV1 Pi Runtime](../cv1-pi-runtime/index.md)
- [CV2 Runtime Portability](../cv2-runtime-portability/index.md)
- [CV3 Pi Skill Parity](../cv3-pi-skill-parity/index.md)
- [CV5 Multisession Safety](../cv5-multisession-safety/index.md)
