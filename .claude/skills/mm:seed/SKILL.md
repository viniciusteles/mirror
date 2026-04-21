---
name: "mm:seed"
description: Seeds identity YAML files into the memory database
user-invocable: true
---

# Seed

Loads identity YAML files (`self`, `ego`, `user`, `organization`, personas, journeys) into the memory database.

```bash
python -m memory seed --env production
```

Use after changing repository identity YAML files to synchronize the database.
