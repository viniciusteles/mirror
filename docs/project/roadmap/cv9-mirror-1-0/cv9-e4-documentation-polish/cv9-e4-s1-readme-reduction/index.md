[< CV9.E4 Documentation & Polish](../index.md)

# CV9.E4.S1 — README Reduction

**Status:** —  
**Epic:** CV9.E4 Documentation & Polish

---

## User-Visible Outcome

A stranger who lands on the Mirror Mind GitHub page reads a focused, compelling
document that answers three questions in under three minutes: what problem does
this solve, why is it different from a generic chatbot layer, and how do I get
started? They are not buried in installation steps, runtime instructions, or
persona tables before they have decided whether to try it.

---

## Problem

`README.md` is currently over 700 lines long. It tries to be the installation
guide, the command reference, the architecture overview, and the extension
tutorial simultaneously. The 12-persona table appears verbatim. The full
per-runtime start instructions are repeated in detail. The extension install,
expose, and smoke test cycle is documented in full.

This creates two problems:

1. **The public hook is buried.** The value proposition — what Mirror Mind is
   and why it matters — is surrounded by operational content that only matters
   to someone who has already decided to use it. A stranger evaluating the
   project has to read through installation steps to find the pitch.

2. **Duplication is guaranteed.** README and Getting Started currently cover
   the same onboarding ground. Any change to the onboarding flow requires
   two edits. This is a structural guarantee of future inconsistency.

---

## Scope

**In scope:**

- Reduce README to a public hook. Target: under 200 lines.
- Keep: problem framing, value proposition ("what changes when you adopt Mirror
  Mind"), credits and lineage, Jungian architecture sketch, prerequisites list,
  a 3–4 command quick start, a pointer to Getting Started, a pointer to
  REFERENCE for commands, and a documentation section linking the full doc set.
- Remove: the detailed `memory init` flow, the 12-persona table, full per-runtime
  start instructions, the extension install/expose/clean cycle, the full commands
  table inline, and the "Setting up your identity" walkthrough.
- The commands table is replaced by a single pointer to `REFERENCE.md`.

**Out of scope:**

- Changes to `docs/getting-started.md` — that is S2.
- Changes to `REFERENCE.md` — that is S3.
- Any new content that does not already exist elsewhere.

---

## Done Condition

- README is under 200 lines.
- A stranger can read it in under 3 minutes and understand what Mirror Mind is
  and why it exists.
- Every piece of content removed from README either already exists in
  `docs/getting-started.md` or will be confirmed to exist when S2 runs.
- The documentation section in README accurately maps the full doc set.
- CI remains green.

---

## Dependencies

None. S1 is the starting point of the E4 sequence.

---

## See also

- [CV9.E4 Documentation & Polish](../index.md)
- [S2 — Getting Started Consolidation](../cv9-e4-s2-getting-started-consolidation/index.md)
