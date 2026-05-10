[< Story](index.md)

# Test Guide — CV13.E1 Docs Browser

## Automated tests

Run:

```bash
uv run pytest tests/unit/memory/web
```

Expected:

```text
all tests pass
```

## Manual smoke test

Start the web console:

```bash
uv run python -m memory web
```

Open:

```text
http://127.0.0.1:8765
```

Expected:

- the left sidebar shows a hierarchical docs tree matching the docs folders
- selecting `Coherence as Product Architecture` loads the document
- headings render as HTML, not raw Markdown
- tables and fenced code blocks render correctly

Stop the server with `Ctrl+C`.

## Safety smoke test

While the server is running, open:

```text
http://127.0.0.1:8765/api/docs/file?path=../.env
```

Expected:

```json
{"error": "..."}
```

and a non-200 response.
