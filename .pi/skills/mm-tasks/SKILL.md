---
name: "mm-tasks"
description: Lists and manages journey tasks
user-invocable: true
---

# Tasks

When receiving `/mm-tasks [subcommand] [args]`:

```bash
python -m memory tasks [subcommand] [args]
```

Subcommands: `list` (default), `add`, `done`, `doing`, `block`, `delete`, `import`, `sync`, `sync-config`

**Examples:**
```bash
python -m memory tasks --journey mirror-poc
python -m memory tasks add "Write plan doc" --journey mirror-poc
python -m memory tasks done <task-id>
```

Present the output to the user without modification.
