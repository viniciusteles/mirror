---
name: "mm-seed"
description: Seeds identity YAML files into the memory database
user-invocable: true
---

# Seed

When receiving `/mm-seed`:

```bash
python -m memory seed --env production
```

Use after changing repository identity YAML files to synchronize the database.
Tell the user the result.
