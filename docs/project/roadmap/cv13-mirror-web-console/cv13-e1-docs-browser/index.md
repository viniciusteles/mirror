[< CV13](../index.md)

# CV13.E1 — Docs Browser

**Status:** Planned
**User-visible outcome:** A local web UI can browse Mirror documentation and
render Markdown as HTML.

---

## Scope

Add a local read-only web console slice:

```bash
uv run python -m memory web
```

The server binds to `127.0.0.1` by default and exposes:

```text
GET /api/docs/tree
GET /api/docs/file?path=...
```

The UI includes:

- a hierarchical sidebar matching the docs folder structure
- a main pane rendering selected Markdown as HTML
- access to `docs/**/*.md` and selected root docs such as `README.md`

---

## Non-goals

- No config editing.
- No identity editing.
- No memory database access.
- No remote hosting.
- No authentication layer yet, because the server is local-only and read-only.

---

## Done Condition

CV13.E1 is done when:

- `uv run python -m memory web` starts the local console.
- The docs tree lists Mirror docs.
- Selecting a doc renders Markdown as HTML.
- Path traversal is rejected.
- Non-doc files outside allowed roots are rejected.
- Unit tests cover docs listing, rendering, and safety checks.

---

## See also

- [Plan](plan.md)
- [Test Guide](test-guide.md)
