# Identity Templates

This directory contains the generic bootstrap templates for a new Mirror Mind user home.

These files are:
- **generic templates**
- **English-first**
- **bootstrap assets only**

These files are **not**:
- live user identity
- the runtime source of truth
- a replacement for the user-owned identity under `~/.mirror/<user>/identity/`

## Where these templates go

Copy or adapt these templates into a real user home:

```text
~/.mirror/<user>/identity/
```

Example:

```bash
mkdir -p ~/.mirror/your-name/identity
cp -R templates/identity/* ~/.mirror/your-name/identity/
```

## Runtime relationship

Mirror Mind seeds identity from the active user home.
It does **not** seed from this repository template directory at runtime.

Runtime source of truth:
- database: `~/.mirror/<user>/memory.db`
- seed source: `~/.mirror/<user>/identity/`

## Structure

```text
templates/identity/
  self/
    config.yaml
    soul.yaml
  ego/
    identity.yaml
    behavior.yaml
  user/
    identity.yaml
  organization/
    identity.yaml
    principles.yaml
  personas/
    writer.yaml
    thinker.yaml
    engineer.yaml
  journeys/
    personal-growth.yaml
```

## Required vs optional identity

Required core identity for seeding:
- `self/`
- `ego/`
- `user/`

Optional:
- `organization/`
- `personas/` — starter lenses for writing, thinking, and engineering
- `journeys/` — starter long-running arc for personal growth

## Starter defaults

The repository ships meaningful starter defaults rather than placeholder files:

- `personas/writer.yaml` — writing, editing, publishing, and voice refinement
- `personas/thinker.yaml` — ideas, decisions, framing, hypotheses, and conceptual clarity
- `personas/engineer.yaml` — software, systems, debugging, tests, and technical design
- `journeys/personal-growth.yaml` — a broadly useful journey for reflection, self-knowledge, and intentional change

These files are safe to seed as-is for a first run. A user can then edit, delete,
or replace them in their own `~/.mirror/<user>/identity/` home before or after
seeding.

## Notes

- Keep these templates generic.
- Do not store real personal identity in this directory.
- If a file starts feeling biographical or private, it belongs in a user home, not in the repo.
