[< Story](index.md)

# Plan — CV13.E1 Docs Browser

## Design

Use the Python standard library HTTP server plus the `markdown` package. Avoid a
frontend build system in the first slice.

Files:

```text
src/memory/web/
  __init__.py
  docs.py
  server.py
  static/
    index.html
    app.js
    style.css
```

Docs API:

```text
GET /api/docs/tree
  returns a hierarchical tree of directory and file nodes

GET /api/docs/file?path=docs/product/envisioning/index.md
  returns { path, markdown, html }
```

Allowed paths:

```text
docs/**/*.md
README.md
REFERENCE.md
CLAUDE.md
AGENTS.md
```

Safety:

- bind to `127.0.0.1` by default
- reject absolute paths
- reject path traversal
- reject non-Markdown files
- reject files outside allowed roots

## Verification

Add unit tests for:

- docs tree listing
- allowed markdown read
- Markdown-to-HTML rendering
- path traversal rejection
- non-doc file rejection

Run:

```bash
uv run pytest tests/unit/memory/web
```
