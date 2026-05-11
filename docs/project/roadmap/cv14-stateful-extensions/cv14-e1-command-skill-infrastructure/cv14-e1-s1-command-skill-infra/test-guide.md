[Roadmap](../../../index.md) › [CV14](../../index.md) › [E1](../index.md) › [S1](plan.md) · **Test Guide**

# CV14.E1.S1 — Test Guide: Command-Skill Infrastructure

**Status:** ✅ Done · all listed verifications executed and green in [PR #7](https://github.com/viniciusteles/mirror/pull/7)

## Canonical test guide

The full per-component test matrix lives in the product user story:

> [US-00 — Command-Skill Infrastructure](../../../../../product/extensions/user-stories/US-00-infra-de-command-skill.md)
> (section **Test Guide**)

It enumerates the cases for each new module — errors, schema bootstrap,
migrations, API DB methods, loader, CLI dispatcher, context registry, Mirror
Mode hook — plus the cross-cutting edge cases every extension must cover.

## Summary of verification performed

The story closed against the following acceptance evidence:

- `uv run pytest tests/unit/memory/extensions/` — 76 extension-specific
  tests, all green.
- `uv run pytest` — full suite at 1103 passed.
- `uv run ruff check src/ tests/` — clean.
- `uv run ruff format --check src/ tests/` — clean (modulo the unrelated
  formatting fix on `src/memory/web/docs.py` cherry-picked from PR #4 to
  unblock CI).
- CI on the post-implementation push: green on Python 3.10 and 3.12,
  run id `25668728695`.
- Manual smoke test against the real user mirror home
  (`~/.mirror/alisson-vale/`): install the fixture, exercise `ping`,
  `list`, `bindings`, `bind --persona tesoureira`, `bindings` again,
  `uninstall`; verify post-uninstall that the binding rows were swept and
  the extension's data table was preserved. Cleaned up the smoke artifacts
  after.

## Acceptance criteria (from [US-00](../../../../../product/extensions/user-stories/US-00-infra-de-command-skill.md))

- [x] `python -m memory extensions install` runs migrations and `register`.
- [x] `python -m memory ext hello ping` works end to end on the fixture.
- [x] `python -m memory ext list` shows installed extensions.
- [x] Binding/unbinding `hello.greeting` to a fixture persona works.
- [x] Mirror Mode with that persona active injects the provider's text.
- [x] All extension-system tests pass.
- [x] Full test suite passes.
- [x] CI green on the post-implementation push.
- [x] AGENTS.md updated with an Extensions section.
- [x] Documentation matches the implementation.

---

**See also:** [Roadmap](../../../index.md) · [CV14](../../index.md) · [CV14.E1](../index.md) · [CV14.E1.S1 Plan](plan.md) · [US-00 (product)](../../../../../product/extensions/user-stories/US-00-infra-de-command-skill.md)
