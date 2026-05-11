# Binding Model

This document explains how extensions connect to the rest of the mirror — to
personas, to journeys, and (in the future) globally. It is the most
conceptually loaded part of the system, so it gets its own document.

## The problem

An extension is generic code. The mirror that installs it has a user-specific
identity: each user has their own personas, their own journeys. An extension
cannot hardcode `"treasurer"` or `"product-launch"` because those names may
not exist in any given mirror.

We need a way for:

- **the extension** to declare *what it can offer* (capabilities),
- **the user** to decide *where each capability shows up* (bindings),
- **the mirror** to invoke the right capability at the right moment
  (dispatch).

## Three concepts

### Capabilities (declared by the extension)

A **capability** is a named hook the extension offers. It is declared in the
manifest and registered at runtime through `api.register_mirror_context`.

A capability is *not* a CLI subcommand. CLI subcommands are always reachable
directly (`python -m memory ext <id> <subcommand>`). Capabilities are
context providers that the mirror calls *on behalf of* a persona.

Example declaration (finance extension):

```yaml
mirror_context_providers:
  - id: financial_summary
    description: "Live financial summary: balances by liquidity, monthly cash flow, runway."
    suggested_personas: [treasurer, cfo, founder]
```

`suggested_personas` is a hint, never a binding. The mirror does not act on it
automatically; it is shown to the user during install to make binding obvious.

### Bindings (decided by the user)

A **binding** maps a capability to a target — typically a persona. Bindings
live in a core table:

```sql
CREATE TABLE _ext_bindings (
  extension_id   TEXT NOT NULL,
  capability_id  TEXT NOT NULL,
  target_kind    TEXT NOT NULL,    -- 'persona' | 'journey' | 'global'
  target_id      TEXT,             -- NULL for 'global'
  created_at     TEXT NOT NULL,
  PRIMARY KEY (extension_id, capability_id, target_kind, target_id)
);
```

The user manages bindings through CLI commands provided by the core (not by
the extension):

```bash
python -m memory ext <id> bind   <capability> --persona <persona_id>
python -m memory ext <id> unbind <capability> --persona <persona_id>
python -m memory ext <id> bindings
```

Multiple bindings per capability are allowed: a capability may be bound to
several personas at once.

### Dispatch (executed by the mirror)

When the mirror assembles a Mirror Mode prompt and the active persona is `P`,
it queries `_ext_bindings WHERE target_kind='persona' AND target_id=P`. For
each match, it loads the corresponding extension (if not loaded), looks up
the capability in the context registry, and calls the provider function with
a `ContextRequest`.

The provider returns either a string (appended to the prompt) or `None`
(skipped silently). Exceptions are caught, logged, and ignored.

## Three target kinds

### `persona` — the primary mechanism

Persona is the most natural binding target because personas are **stable
identity slots**. They are declared once in the user's identity and rarely
change. They are also already the routing surface the mirror uses to decide
*how to respond* — extending them with extra context is a natural fit.

Use persona bindings for capabilities that should fire whenever a specific
expression of the user is active:

- finance summary → bound to `treasurer`,
- recent testimonials → bound to `writer` or `marketer`,
- upcoming class agenda → bound to `teacher`.

### `journey` — for journey-scoped context

Journeys are *data*, not identity. They come and go. A journey-scoped binding
is useful when a capability only makes sense in the context of a specific
ongoing journey — for example, an extension that tracks the metrics of one
product launch and should only inject when that journey is active.

Concretely, the dispatcher inspects the request's `journey_id`. If a binding
exists for `target_kind='journey'` and `target_id=<journey_id>`, the provider
fires.

Most extensions will not use journey bindings. They are reserved for narrow
cases where the data and the journey have a one-to-one relationship.

### `global` — reserved for the future

A binding with `target_kind='global'` would fire on every Mirror Mode turn,
regardless of persona or journey. This is rejected during Phase 1 because the
cost of polluting every prompt usually outweighs the benefit. The schema
supports it, the dispatch does not. A later phase may enable it for narrow,
opt-in cases (a privacy notice, a hard constraint reminder).

## Data flow at a Mirror Mode turn

```
user query
   │
   ▼
detect_persona(query)  ─────→  active_persona = "treasurer"
   │
   ▼
load_mirror_context(persona="treasurer", journey="eudaimon", query=...)
   │
   ├─ assemble core sections (self, ego, persona, journey, attachments, ...)
   │
   ├─ collect_extension_context(persona="treasurer", journey="eudaimon", ...)
   │     │
   │     ├─ SELECT * FROM _ext_bindings
   │     │     WHERE (target_kind='persona' AND target_id='treasurer')
   │     │        OR (target_kind='journey'  AND target_id='eudaimon')
   │     │
   │     ├─ for each (ext_id, capability_id):
   │     │     ├─ load extension (if needed)
   │     │     ├─ provider = context_registry[(ext_id, capability_id)]
   │     │     ├─ text = safely_call(provider, ContextRequest(...))
   │     │     └─ if text: append "=== extension/<id>/<cap> ===\n<text>"
   │
   ▼
return assembled prompt
```

## Why not auto-bind from `suggested_personas`?

It would feel convenient. We reject it for three reasons:

1. **Surprise.** A user installs an extension and suddenly their prompt
   doubles in size. Auto-binding hides cost.
2. **Wrong defaults.** The extension author cannot know the user's persona
   set. A suggestion is informational, not authoritative.
3. **Reversibility.** Manual binding is also manual unbinding, with no hidden
   state to track down.

The install command may *print* the suggested personas and prompt the user to
bind, but it never binds silently.

## Why CLI direct invocation does not need bindings

CLI subcommands (`python -m memory ext finances runway`) are always reachable
without any binding. They are not part of the binding model. The agent (or
the user) calls them explicitly when needed. Bindings exist solely to control
*automatic* context injection during Mirror Mode.

A capability and a CLI subcommand are independent surfaces. An extension may
offer:

- only CLI subcommands (no Mirror Mode integration),
- only context providers (rare; usually combined with CLI),
- both, with overlap (the provider's text and the subcommand's output share
  underlying functions but are presented differently).

## Failure modes and how the mirror handles them

| Failure | Behavior |
|---|---|
| Provider raises an exception | Caught, logged, skipped. Prompt continues without this section. |
| Provider returns very long text | Returned as-is. Truncation is the extension's responsibility. |
| Extension fails to load | All its bindings are inert for this turn. Logged. |
| Binding refers to a deleted extension | Logged once per process, then ignored. Cleaned up by `extensions prune`. |
| Binding refers to a non-existent persona | Never fires (the persona is never the active one). No error. |

The user is never blocked. The mirror always responds.
