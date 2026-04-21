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
    _template.yaml
  journeys/
    _template.yaml
```

## Required vs optional identity

Required core identity for seeding:
- `self/`
- `ego/`
- `user/`

Optional:
- `organization/`
- `personas/`
- `journeys/`

## Notes

- Keep these templates generic.
- Do not store real personal identity in this directory.
- If a file starts feeling biographical or private, it belongs in a user home, not in the repo.
