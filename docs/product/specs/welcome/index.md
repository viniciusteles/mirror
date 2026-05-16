[< Specs](../index.md)

# Welcome Card

A short, state-aware message the mirror surfaces once when a runtime starts.
Replaces nothing essential — it is not a banner or a menu. It exists to make
the mirror feel **continuous** across sessions: when you open it, you should
sense that something already lives there.

The welcome is computed by the Python core and rendered by each runtime as a
single block. One source, four interfaces, one voice.

---

## Principles

1. **One unit, not many.** Welcome appears in one place per startup. Never
   duplicated between popup and footer, never split into a sequence of
   notifications.
2. **State, not decoration.** Content reflects the current state of the mirror
   (active journey, recent insight, recent conversation). Static banners are
   forbidden.
3. **Silence when there is no signal.** If the mirror has nothing meaningful
   to say, the welcome is empty and nothing renders. The command must be safe
   to call in any state.
4. **Local and cheap.** Welcome composition is pure SQLite reads. No LLM, no
   network, no embeddings. Must run in well under 100 ms on a warm database.
5. **First person.** The mirror speaks as the user. The closing invitation is
   not "How can I help you?" — it is `Where shall we begin?`.

---

## Anatomy

The welcome has up to **four lines** plus a closing invitation:

```
◇ Mirror · <user>
Active journey: <slug> — <stage> · next: <next>
<context line>

→ Where shall we begin?
```

| Line | When it appears | Source |
|------|-----------------|--------|
| Header (`◇ Mirror · <user>`) | Always, if a Mirror home is resolvable | `resolve_mirror_home().name` |
| Active journey | If at least one journey identity has `Status: active` | `list_active_journeys()` + `get_journey_path()` |
| Context | Conditional — see below | recent memories or conversations |
| Invitation (`→ Where shall we begin?`) | Always | constant |

If the header cannot be resolved (no `MIRROR_HOME`, no `MIRROR_USER`), the
welcome is empty.

### Choosing the active journey

When multiple journeys are active, the welcome picks the one most recently
engaged. The order of preference is:

1. Journey of the most recent conversation
2. Journey of the most recent memory
3. First active journey returned by `list_active_journeys()`

This reflects the spirit of "where the mirror is currently engaged" rather
than an alphabetical accident.

### Choosing the context line

The third line adapts to the state. The first rule that matches wins:

1. **Last insight** — if there is a memory in the active journey with
   `layer in (self, ego)` created in the last 30 days, render its title:
   `Last insight: "<title>"`.
2. **Last conversation** — else, if there is a conversation in the active
   journey that ended within the last 48 hours, render relative time and
   title: `Last conversation <N>h ago — <title>` (falls back to summary or
   "untitled").
3. **Nothing** — omit the line entirely. The welcome stays two-line.

This keeps the welcome useful when there is state, and quiet when there isn't.

### Stage and next

The "Active journey" line includes stage and next-action extracted from the
journey path identity with the same regex patterns used by
`memory journeys`:

- Stage: `**Current stage:**` / `**Etapa atual:**` / `**Fase:**`
- Next: `**Next:**` / `**Next action:**` / `**Próximo:**` / `**Próxima ação:**`

If a part is missing, that fragment is dropped. The line never has dangling
separators (no `— ·`).

---

## Contract: `python -m memory welcome`

Prints the composed welcome to stdout and exits 0. Always exits 0 even when
no welcome is produced (empty output).

```
Usage: python -m memory welcome [--mirror-home PATH]
```

Behaviour:

- Reads the active Mirror home from `--mirror-home`, `MIRROR_HOME`, or
  `MIRROR_USER` (standard resolution).
- Emits an empty string if `MIRROR_WELCOME=off` is set.
- Emits an empty string if the Mirror home cannot be resolved.
- Otherwise composes the welcome per the rules above.

Stdout is the rendering. There is no JSON variant. Runtimes must not parse —
they just display the string verbatim.

---

## Runtime integration

Each runtime calls `python -m memory welcome` once at session start. The
display rules are:

| Runtime | Render | Notes |
|---------|--------|-------|
| Pi | `ctx.ui.notify(welcome, "info")` once if non-empty | Status bar shows `<user> · <Nj>` separately |
| Codex | `printf` to terminal once if non-empty | Same string |
| Gemini CLI | `printf` to terminal once if non-empty | Same string |
| Claude Code | `/mm:welcome` skill prints it on demand | No automatic injection |

Pi must not also notify the session-start summary string (logging status,
extraction counts) — that information stays in the footer status. The welcome
is the only popup.

---

## Skills

`/mm-welcome` (Pi, Gemini), `$mm-welcome` (Codex), `/mm:welcome` (Claude Code)
all invoke the same command. Useful when:

- `quietStartup: true` is on and the user wants to see the welcome
- The user wants a snapshot mid-session
- A new runtime starts and the welcome was missed
