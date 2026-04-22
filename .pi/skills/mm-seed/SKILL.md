---
name: "mm-seed"
description: Seeds identity YAML files into the memory database
user-invocable: true
---

# Seed

When receiving `/mm-seed`:

```bash
uv run python -m memory seed --env production
```

Use after changing user-home identity YAML files to synchronize the database.
Tell the user the result.
