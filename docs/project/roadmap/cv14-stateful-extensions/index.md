[Roadmap](../index.md) › **CV14 Stateful Extension System**

# CV14 — Stateful Extension System

**Status:** 🟢 Phase 1 Done · E2–E4 planned
**Goal:** Let user-specific features that need their own database tables, CLI surface, and Mirror Mode integration live as installable extensions, fully outside the core repository, while reusing the mirror's storage, embeddings, LLM router, and persona routing.

---

## What This Is

[CV6.E5](../cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md)
closed the door on user-specific capabilities accidentally landing in core by
defining the **prompt-skill** extension model: a markdown manifest that
orchestrates existing Mirror commands, with `review-copy` as the reference
path. That solved the simple case — workflows with no state.

This CV picks up where
[CV6.E5](../cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md)
stopped. Real user features tend to need more than prompt orchestration: a
finance tracker needs tables for accounts and transactions, importers, a
runway calculator, and a way to surface that data to the Mirror at
conversation time. A testimonials tool needs persistent records, embeddings,
and semantic search. These are stateful capabilities, and they need a real
contract:

- their own SQLite tables under a forced `ext_<id>_*` prefix
- a Python entrypoint with `register(api)` that receives a stable API surface
- SQL migrations versioned and checksum-tracked
- a CLI dispatcher (`python -m memory ext <id> <subcommand>`)
- a binding model that wires extension capabilities to user-defined personas
- automatic Mirror Mode context injection, with isolated failure modes

This CV delivers exactly that contract, in phases that match the
[product extensions roadmap](../../../product/extensions/roadmap.md). Phase 1
ships the full `command-skill` infrastructure and an end-to-end fixture; later
phases polish authoring, add cross-extension features, and explore
distribution.

This CV is about **platform capability**: the mirror gains the ability to host
stateful extensions safely. Specific extensions a user might write (finance,
testimonials, etc.) are not part of this CV — they live in the user's own
repository and have their own user-story trail there.

---

## Relationship to [CV6.E5](../cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md)

[CV6.E5](../cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md)
— **prompt-skill** model — remains valid and Done. It is the right choice for
stateless workflows. This CV — **command-skill** model — is the stateful
complement. The manifest validator accepts both `kind` values; extension
authors choose the simpler one when no state is needed.

Conceptually, CV14 is the successor of
[CV6.E5](../cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md)
for the stateful case. They coexist without conflict in the codebase.

---

## Epics

| Code | Epic | User-visible outcome | Status |
|------|------|----------------------|--------|
| [CV14.E1](cv14-e1-command-skill-infrastructure/index.md) | Command-skill infrastructure | Authors can write, install, and run stateful extensions end to end | ✅ Done |
| CV14.E2 | Authoring quality of life | Scaffolding tooling, better error messages, doctor command, schema dumps | 🟡 Planned |
| CV14.E3 | Cross-extension features | Event bus, cross-extension reads, optional `target_kind=global` bindings, cost accounting | ⚪ Provisional |
| CV14.E4 | Distribution | Package format, remote install, sharing flow between users | ⚪ Provisional |

The phase boundaries match the
[product extensions roadmap](../../../product/extensions/roadmap.md). E3 and
E4 are not committed; they will be planned only when E2 closes and concrete
evidence of need is available.

---

## Done Condition (for the CV as a whole)

This CV does not aim to be "Done" as a single moment. It is delivered as its
epics close. The CV is considered fully delivered when
[E1](cv14-e1-command-skill-infrastructure/index.md) and E2 are Done; E3 and
E4 are explicitly optional and will be re-evaluated then.

[E1](cv14-e1-command-skill-infrastructure/index.md) specifically is done. See
its [index](cv14-e1-command-skill-infrastructure/index.md) for criteria and
verification.

---

## Out of Scope

- specific user-owned extensions (a `finances` extension, a `testimonials`
  extension, etc.) — these live in the user's own repository and are tracked
  in that repository's user-story trail, not here
- a marketplace or central registry of extensions
- hot-reload of extensions inside a running process
- sandboxing beyond the table-prefix contract (extensions are trusted code
  installed explicitly by the user)
- prompt-skill scope, already delivered by
  [CV6.E5](../cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md)

---

## Sequencing

```text
E1 Command-skill infrastructure   (Done)
  └── E2 Authoring quality of life
       └── E3 Cross-extension features      (provisional)
            └── E4 Distribution             (provisional)
```

[E1](cv14-e1-command-skill-infrastructure/index.md) unblocks the construction
of any stateful extension a user wants to write. E2 is incremental polish; it
sharpens the authoring experience based on learnings from the first real
extensions. E3 and E4 are gated on evidence.

---

**See also:** [Roadmap](../index.md) · [CV6.E5 Extension Model (prompt-skill)](../cv6-intelligence-runtime-maturity/cv6-e5-extension-model/index.md) · [Product · Extensions](../../../product/extensions/index.md)
