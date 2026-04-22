---
name: "mm-journey"
description: Shows detailed journey status and optionally updates the journey path
user-invocable: true
---

# Journey

When receiving `/mm-journey [slug]`:

```bash
uv run python -m memory journey [slug]
```

When receiving `/mm-journey update <slug> <content>`:

```bash
uv run python -m memory journey update <slug> "<content>"
# or pipe via stdin:
echo "<content>" | uv run python -m memory journey update <slug> -
```

Present the output to the user.
