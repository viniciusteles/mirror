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
    constraints.yaml
  user/
    identity.yaml
  organization/
    identity.yaml
    principles.yaml
  personas/
    coach.yaml
    designer.yaml
    doctor.yaml
    engineer.yaml
    financial.yaml
    prompt-engineer.yaml
    researcher.yaml
    strategist.yaml
    teacher.yaml
    therapist.yaml
    thinker.yaml
    writer.yaml
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
- `personas/` — 12 starter lenses covering the most common domains
- `journeys/` — starter long-running arc for personal growth

## Starter defaults

All templates ship with real, opinionated content — not placeholder fill-in forms.
`memory init <name>` followed by `memory seed` produces a working mirror with
no manual editing required.

The `{{user_name}}` token in `self/soul.yaml` and `user/identity.yaml` is
replaced automatically with the user's name during `memory init`.

### Personas (12)

| File | Domain |
|------|--------|
| `writer.yaml` | Writing, editing, voice, publishing |
| `thinker.yaml` | Ideas, decisions, conceptual clarity, framing |
| `engineer.yaml` | Software, systems, debugging, architecture |
| `therapist.yaml` | Emotional processing, patterns, inner work |
| `strategist.yaml` | Business positioning, decisions, trade-offs |
| `coach.yaml` | Accountability, goals, habits, momentum |
| `researcher.yaml` | Inquiry, synthesis, evidence, analysis |
| `teacher.yaml` | Pedagogy, explanation, curriculum, mentoring |
| `doctor.yaml` | Health, symptoms, medical literacy |
| `financial.yaml` | Money, budgeting, investment, financial decisions |
| `designer.yaml` | Product design, UX, visual design, creative direction |
| `prompt-engineer.yaml` | Prompt design, AI system architecture, Mirror self-improvement |

### Journey

- `journeys/personal-growth.yaml` — a broadly useful journey for reflection,
  self-knowledge, and intentional change

## Notes

- Keep these templates generic.
- Do not store real personal identity in this directory.
- If a file starts feeling biographical or private, it belongs in a user home, not in the repo.
