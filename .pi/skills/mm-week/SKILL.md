---
name: "mm-week"
description: Shows the weekly view or ingests a free-text plan
user-invocable: true
---

# Week

When receiving `/mm-week` (no arguments):

```bash
python -m memory week
```

When receiving `/mm-week plan "<free text>"`:

```bash
python -m memory week plan "<free text>"
```

This calls an LLM to extract temporal items. After showing the extracted items,
ask the user to confirm before saving. If confirmed:

```bash
python -m memory week save
```

Present all output to the user without modification.
