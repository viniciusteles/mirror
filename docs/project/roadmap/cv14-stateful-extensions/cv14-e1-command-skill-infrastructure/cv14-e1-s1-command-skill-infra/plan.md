[Roadmap](../../../index.md) › [CV14](../../index.md) › [E1](../index.md) › **S1 · Plan**

# CV14.E1.S1 — Plan: Command-Skill Infrastructure

**Status:** ✅ Done · delivered in [PR #7](https://github.com/viniciusteles/mirror/pull/7)

## Canonical plan

The substantive plan lives in the product documentation alongside the rest of
the extension system specification:

> [US-00 — Command-Skill Infrastructure](../../../../../product/extensions/user-stories/US-00-infra-de-command-skill.md)

That document carries the full **Story / Plan / Test Guide** for this delivery:
narrative motivation, list of files added or changed, sequenced TDD
implementation steps, and the testing matrix per component.

The story is intentionally not duplicated here. Keeping the canonical
specification in `docs/product/extensions/` means:

- the spec lives next to every other document that describes how the
  extension system works (architecture, API reference, binding model,
  migrations contract, authoring guide, testing guide),
- a reader who lands on the extension documentation sees the story in
  context, not as an isolated roadmap fragment,
- the project roadmap stays focused on what it does well — sequencing,
  status, dependencies — without becoming a second source of truth.

## What this entry tracks

- **Where:** [CV14.E1](../index.md) of the project roadmap.
- **What:** the single story that closed [E1](../index.md) of
  [CV14](../../index.md).
- **Status:** Done, 2026-05-11.
- **Pull request:** [#7 — Design and implement the command-skill extension system (Phase 1)](https://github.com/viniciusteles/mirror/pull/7)

## Headline scope (for quick reference)

End-to-end infrastructure for stateful extensions:

- `_ext_migrations` and `_ext_bindings` core tables;
- `memory.extensions.{errors,api,migrations,loader,context}`;
- `memory.cli.ext` dispatcher;
- updated manifest validator (`entrypoint.module`, `table_prefix` consistency);
- `install` runs migrations and validates `register(api)`;
- `uninstall` sweeps orphan bindings, preserves data tables;
- Mirror Mode hook in `IdentityService.load_mirror_context`;
- fixture `ext-hello` exercising the full contract;
- 95 new tests; suite at 1103 passing.

For the full breakdown and rationale per change, see the
[canonical user story](../../../../../product/extensions/user-stories/US-00-infra-de-command-skill.md)
and the [PR description](https://github.com/viniciusteles/mirror/pull/7).

---

**See also:** [Roadmap](../../../index.md) · [CV14](../../index.md) · [CV14.E1](../index.md) · [CV14.E1.S1 Test Guide](test-guide.md) · [US-00 (product)](../../../../../product/extensions/user-stories/US-00-infra-de-command-skill.md)
