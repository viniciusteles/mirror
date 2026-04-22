---
name: "mm-mirror"
description: Activates Mirror Mode — loads identity, persona, attachments, and records response
user-invocable: true
---

# Mirror Mode

Use this procedure to answer in Mirror Mode. `CLAUDE.md` routing determines when
to activate it; this skill defines how.

---

> ⛔ **HARD CONSTRAINT**
> Never produce a Mirror Mode response without first running `uv run python -m memory mirror load`.
> No exceptions. Load first. Always.

---

> ⚠️ **NO QUERY YET?**
> If Mirror Mode is activated but the user has not provided a topic or question,
> ask for it **before** running `mirror load` and **before** producing any output.
> Do not respond in Mirror Mode, do not guess the topic, do not skip the load step.
> Ask first. Load after. Answer last.

---

## 1. Load Context

This is always the first action, before any visible output to the user.

```bash
uv run python -m memory mirror load \
  --query "full text of the user's prompt" \
  [--persona PERSONA_ID] \
  [--journey JOURNEY_ID] \
  [--org]
```

The script:
- Auto-detects journey and persona from `--query` when not specified
- Prints loaded identity plus relevant attachments (score > 0.4)
- Uses session-scoped routing only when the runtime passes an explicit `--session-id`

Pass `--journey` and `--persona` explicitly when known with confidence. When
uncertain, omit them and let auto-detection decide.

**Examples:**
- Generic query: `--query "I need to define the next article topic"`
- Known journey: `--journey mirror --query "how should I approach the next epic"`
- With persona: `--persona writer --query "review this article draft"`
- With organization: `--org --query "course launch strategy"`

## 2. Answer

Use the `load` output as the complete response context.

- Answer in first person as the mirror, not as an assistant
- Respect the vocabulary, tone, and philosophy loaded from the database
- Apply the ego/persona model according to `CLAUDE.md`

## 3. Record Response

If the runtime exposes a session-aware logging path, record a concise 2–3 sentence summary there. In Pi, the extension already records assistant turns safely, so do not fabricate a session id just to call `mirror log`.
