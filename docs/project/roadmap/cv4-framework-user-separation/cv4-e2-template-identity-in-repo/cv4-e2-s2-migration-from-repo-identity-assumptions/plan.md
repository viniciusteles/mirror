[< CV4.E2 Template Identity in Repo](../index.md)

# CV4.E2.S2 — Plan: Migration from repo-owned identity assumptions to `templates/identity/`

## What and Why

CV4.E2.S1 defines what a template is. This story plans the transition from the
current repository-owned identity layout to that template-only model.

Today the repo still contains real identity material under:

```text
identity/
  self/
  ego/
  user/
  organization/
  personas/
  journeys/
```

That content is currently shaped around one real user's mirror. CV4 must not
just move those files into `templates/identity/` mechanically. It must decide:
- what can be generalized into templates
- what must be rewritten as placeholders/examples
- what must leave the repo entirely
- how current seeding assumptions transition safely while implementation is in progress

This story is about planning that migration deliberately rather than treating it
as a bulk file move.

---

## Current Material To Classify

The current repo-owned identity surface includes:

- `identity/self/config.yaml`
- `identity/self/soul.yaml`
- `identity/ego/identity.yaml`
- `identity/ego/behavior.yaml`
- `identity/user/identity.yaml`
- `identity/organization/identity.yaml`
- `identity/organization/principles.yaml`
- persona YAMLs under `identity/personas/`
- journey YAMLs under `identity/journeys/`

These files are not equal in migration difficulty.

### Likely easiest to generalize
- structural/config files with little or no personal biography
- `_template`-style persona/journey examples to be created from scratch

### Highest-risk to template mechanically
- `self/soul.yaml`
- `user/identity.yaml`
- personas like `engineer.yaml` that encode Vinícius-specific biography and operating model
- journeys under `identity/journeys/` that are clearly tied to current personal projects

---

## Proposed Migration Strategy

### 1. Treat current `identity/` as source material, not as target content

The current files should be reviewed one by one and classified into one of
three buckets:

#### A. Generalize into template
Content can be rewritten into a genuinely generic example/template while
preserving useful structure.

#### B. Replace with fresh template
The existing file is too personal; create a new template from scratch instead of
trying to sanitize the old one line by line.

#### C. Remove from repo-owned identity
The content is personal enough that it should not survive in any repo template
form. It belongs only in a real user home.

### 2. Prefer structural preservation over textual preservation

The most valuable thing to carry forward is often the *shape* of the file:
- field names
- section structure
- intended semantics

Not the actual prose.

### 3. Assume many current personas and journeys will be replaced, not sanitized

This is the key design stance. It is safer to create a small number of generic
examples than to keep many personalized artifacts after partial redaction.

### 4. Keep compatibility explicit during transition

Until CV4.E3 implements external identity loading, the codebase may still have
short-term assumptions about `identity/` in the repo. Those should be treated
as transition behavior only, not as a reason to weaken the target architecture.

---

## Recommended Classification Direction

### `self/`
- `config.yaml`: likely **A** (generalize into template)
- `soul.yaml`: likely **B** or **C** depending on how much generic scaffold is useful

### `ego/`
- `behavior.yaml`: likely **A** if rewritten generically
- `identity.yaml`: likely **B** if current prose is too personal

### `user/`
- `identity.yaml`: likely **B** or **C** — very high personal-content risk

### `organization/`
- likely **A** if reduced to generic organizational placeholders

### `personas/`
- most current persona files are likely **B**
- better to create a small set of generic examples plus a `_template` file than to sanitize biographies

### `journeys/`
- current journey files are likely **C** as repo content
- better to create one or two generic journey examples or `_template` files from scratch

---

## Questions This Story Should Settle

1. Should the existing `identity/` directory be removed entirely once templates exist, or retained temporarily during migration?
2. Which current files are worth generalizing vs. rewriting from scratch?
3. How many generic example personas/journeys should ship with the repo?
4. Should `_template.yaml` become the norm for personas and journeys in the repo template set?
5. What documentation should explain the difference between migrated source material and final template assets?

---

## Recommended Direction

- do not mechanically rename `identity/` to `templates/identity/`
- classify current files before any relocation work
- preserve structure aggressively, preserve prose selectively
- prefer fresh generic templates over redacted personal documents
- keep the final template set small, strong, and clearly generic
- remove the old repo-owned live-identity model as soon as the replacement path is ready

---

## Deliverable

This story should produce planning/docs that define:
- the migration approach from current `identity/` assumptions to `templates/identity/`
- the classification framework for current identity files
- the standard for deciding rewrite vs. sanitize vs. remove

Implementation belongs to later stories.

---

## Risks and Design Concerns

### 1. Redaction theater
A file can be scrubbed of names and still remain obviously personal in worldview,
voice, and implied biography.

### 2. Over-preserving current content
Trying to save too much of the current repo identity would undermine CV4.

### 3. Under-preserving useful structure
Throwing everything away would also be wasteful if the existing file structures
teach the right shape well.

### 4. Transition confusion
If the docs do not distinguish current transitional `identity/` assumptions from
final `templates/identity/`, the architecture will get muddy again.

---

## Follow-on Work Enabled

Once S2 is accepted, later stories can plan:
- actual creation of `templates/identity/`
- removal or deprecation of repo-owned live-identity assumptions
- bootstrap flows from templates into `~/.mirror/<user>/identity/`
- compatibility handling while CV4.E3 is being implemented
