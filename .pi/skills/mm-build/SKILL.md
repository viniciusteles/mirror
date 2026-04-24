---
name: "mm-build"
description: Activates Builder Mode for a journey and loads project context/docs
user-invocable: true
---

# Builder Mode

Activates Builder Mode for a specific journey. Loads identity context and project docs.

## Usage

```
/mm:build <journey-slug>
```

**Example:** `/mm-build my-journey`

---

## 1. Load Context (DB)

```bash
uv run python -m memory build load <slug>
```

The command:
- Prints identity context (soul + ego + user + journey, persona=engineer)
- Prints relevant memories
- Starts a new database conversation session
- Emits `project_path=<path>` as the last output line

## 2. Read Project Docs

Parse `project_path` from the last output line above. Then read the project docs directly using file tools:

- `<project_path>/docs/README.md`
- `<project_path>/docs/architecture.md`
- `<project_path>/docs/data-model.md`
- `<project_path>/docs/wireframes/*.md`
- `<project_path>/docs/decisions/*.md`

If `project_path` is not set, skip this step and proceed - the journey has no associated project yet.

## 3. Work In Builder Mode

- Work from `project_path` - read, edit, and create project files normally
- Keep project docs updated as the code evolves
- Commit at the end of each session with a descriptive English commit message

## 4. Project Docs Structure

Every project associated with a journey should have:

```
<project_path>/
  docs/
    README.md          - overview: goal, stack, how to run
    architecture.md    - system architecture (Mermaid diagrams)
    data-model.md      - data model, entities, relationships
    wireframes/
      *.md             - screen/component wireframes (Mermaid or ASCII)
    decisions/
      *.md             - ADRs (Architecture Decision Records)
```

**Diagram format:** Mermaid blocks in Markdown.

**When to update docs:**
- `README.md`: stack, setup, or goal changes
- `architecture.md`: services or layers are added/removed
- `data-model.md`: models or migrations change
- `wireframes/`: screens or flows change
- `decisions/`: non-obvious architecture decisions are made

## 5. Configure `project_path`

If the journey does not yet have an associated project:

```bash
uv run python -m memory journey set-path <slug> /path/to/project
```

## 6. Finalize Session

When the user says "End the session":

```bash
uv run python -m memory mirror log "SESSION_SUMMARY"
```
