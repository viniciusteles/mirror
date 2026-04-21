---
name: "mm:review-copy"
description: Sends copy to multiple LLMs and generates structured HTML reviews
user-invocable: true
---

# Review Copy

> Note: this skill is currently treated as a **reference extension example**,
> not as a core Mirror Mind framework capability. It remains in-repo
> temporarily while the extension model matures. The first external-skill
> reference tree now lives at `examples/extensions/review-copy/` and maps to
> `ext:review-copy` for Claude Code.

Sends a copy file to a set of models through OpenRouter and generates an HTML
document with structured reviews, synthesis, and a recommended path.

## Syntax

```
/mm:review-copy <file> <model1> [model2] [model3] ...
```

- **file** - path to the copy text file (`.txt`, `.md`, etc.)
- **models** - one or more models in `family` or `family tier` format. Examples:
  - `grok` or `grok flagship`
  - `llama flagship`
  - `deepseek mid`
  - `gemini` (uses `flagship` by default)

**Examples:**

```
/mm:review-copy ~/Downloads/lp_v9.txt grok flagship, llama flagship, deepseek flagship
/mm:review-copy ~/copy.txt gemini, openai flagship, deepseek
```

When tier is omitted, use `flagship` as the default for copy review.

## Flow

### 1. Read The File

Read the specified file content.

### 2. Identify journey and context

Analyze the file name and content to infer the related journey, such as `uncle-vinny` or `reflexo`. If identified, use `--journey` in the command.

### 3. Build The Review Prompt

Use this standard prompt, inserting the copy content:

```
Review the following copy as a world-class copywriter. I am the author and want radical honesty — no flattery, only what sharpens the blade.

Structure your response in exactly three sections:

(1) WHAT WORKS WELL
List the strongest elements — what is already effective, resonant, or well-crafted.

(2) WHAT COULD IMPROVE
List specific weaknesses — what is redundant, unclear, emotionally flat, or structurally weak.

(3) TOP 5 SUGGESTIONS
Give 5 specific, actionable suggestions. Each should include what to change and why. If relevant, provide actual rewrite examples.

---
COPY:

{COPY_CONTENT}
```

### 4. Ask The Models In Parallel

For each specified model, run:

```bash
python -m memory consult FAMILY TIER "PROMPT" \
  [--journey JOURNEY_ID]
```

Run all calls in parallel using multiple simultaneous tool calls. Capture each model's full response, between `--- response via ... ---` and `--- end ---`.

### 5. Generate The HTML

Generate an HTML document using the template below. Save the output file at
`~/Downloads/<copy-name>_AI_Reviews_<date>.html`.

#### Template HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{TITLE} — AI Copy Reviews</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f4f0; color: #1a1a1a; line-height: 1.6; padding: 40px 24px;
    }
    header { max-width: 1100px; margin: 0 auto 48px; }
    header h1 { font-size: 1.6rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 6px; }
    header p { font-size: 0.92rem; color: #666; }
    .columns {
      display: grid;
      grid-template-columns: repeat({N_COLS}, 1fr);
      gap: 24px; max-width: 1100px; margin: 0 auto 56px;
    }
    .card {
      background: #fff; border-radius: 12px; padding: 28px;
      display: flex; flex-direction: column; box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }
    .card-header {
      display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
      padding-bottom: 16px; border-bottom: 1px solid #eee;
    }
    .model-badge {
      display: inline-block; font-size: 0.7rem; font-weight: 600;
      letter-spacing: 0.08em; text-transform: uppercase;
      padding: 3px 10px; border-radius: 20px;
    }
    /* Badge colors — add as needed */
    .badge-grok     { background: #fce4ec; color: #c62828; }
    .badge-llama    { background: #ede7f6; color: #4527a0; }
    .badge-deepseek { background: #e0f7fa; color: #006064; }
    .badge-gemini   { background: #e8f5e9; color: #1b5e20; }
    .badge-openai   { background: #e3f2fd; color: #0d47a1; }
    .badge-claude   { background: #fff3e0; color: #e65100; }
    .card h2 { font-size: 1rem; font-weight: 700; }
    .section-label {
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: #999; margin: 18px 0 8px;
    }
    .section-label:first-of-type { margin-top: 0; }
    .card p, .card li { font-size: 0.88rem; color: #333; margin-bottom: 6px; }
    .card ul { padding-left: 16px; }
    .card li { margin-bottom: 4px; }
    .highlight {
      background: #fffbea; border-left: 3px solid #f0c040;
      padding: 10px 14px; border-radius: 4px; font-size: 0.88rem; margin: 12px 0;
    }
    .card-footer { margin-top: auto; padding-top: 20px; }
    .btn-full {
      width: 100%; padding: 10px 16px; border: 1.5px solid #1a1a1a;
      background: transparent; border-radius: 8px; font-size: 0.82rem;
      font-weight: 600; cursor: pointer; letter-spacing: 0.02em; transition: all 0.15s;
    }
    .btn-full:hover { background: #1a1a1a; color: #fff; }
    .synthesis {
      max-width: 1100px; margin: 0 auto;
      background: #1a1a1a; color: #f0ede6; border-radius: 12px; padding: 40px 44px;
    }
    .synthesis h2 { font-size: 1.2rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 6px; color: #fff; }
    .synthesis .subtitle { font-size: 0.85rem; color: #999; margin-bottom: 32px; }
    .synthesis-block { margin-bottom: 28px; }
    .synthesis-block h3 {
      font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: #f0c040; margin-bottom: 12px;
    }
    .synthesis-block p { font-size: 0.9rem; color: #ccc; margin-bottom: 8px; }
    .synthesis-block ul { padding-left: 18px; }
    .synthesis-block li { font-size: 0.9rem; color: #ccc; margin-bottom: 6px; }
    .synthesis-block li strong { color: #fff; }
    .modal-overlay {
      display: none; position: fixed; inset: 0;
      background: rgba(0,0,0,0.6); z-index: 100;
      align-items: center; justify-content: center; padding: 24px;
    }
    .modal-overlay.active { display: flex; }
    .modal {
      background: #fff; border-radius: 12px; max-width: 680px; width: 100%;
      max-height: 80vh; overflow-y: auto; padding: 36px; position: relative;
    }
    .modal h3 { font-size: 1rem; font-weight: 700; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid #eee; }
    .modal-body { font-size: 0.88rem; color: #333; line-height: 1.7; white-space: pre-wrap; }
    .modal-close {
      position: absolute; top: 16px; right: 20px; background: none; border: none;
      font-size: 1.3rem; cursor: pointer; color: #666; line-height: 1;
    }
    .modal-close:hover { color: #000; }
    @media (max-width: 768px) {
      .columns { grid-template-columns: 1fr; }
      .synthesis { padding: 28px 24px; }
    }
  </style>
</head>
<body>

<header>
  <h1>{TITLE} — AI Copy Reviews</h1>
  <p>{SUBTITLE}</p>
</header>

<div class="columns">
  <!-- {N} model cards here, one per model -->
</div>

<!-- SYNTHESIS -->
<div class="synthesis">
  <h2>Synthesis — {SYNTHESIS_TITLE}</h2>
  <p class="subtitle">What the models converged on, where they diverged, and the recommended next step.</p>
  <!-- synthesis-blocks here -->
</div>

<!-- MODALS -->
<!-- one modal per model, with full response -->

<script>
  function openModal(id) { document.getElementById(id).classList.add('active'); }
  function closeModal(id) { document.getElementById(id).classList.remove('active'); }
  document.querySelectorAll('.modal-overlay').forEach(el => {
    el.addEventListener('click', e => { if (e.target === el) el.classList.remove('active'); });
  });
</script>
</body>
</html>
```

#### HTML Rules

**Cards** (one per model in the grid):
- `.model-badge` with the correct family color class (`.badge-grok`, `.badge-deepseek`, etc.)
- `h2` heading with the provider name, such as "xAI", "Meta", "DeepSeek", "Google", "OpenAI", or "Anthropic"
- Sections extracted from the response: `What works well` (`ul` list), `What could improve` (`ul` list), `.highlight` with one striking quote from the response, and `Top suggestions` (`ul` list with `strong` on each item title)
- Footer button `Read full response` opens the modal

**Synthesis** (dark final section):
- synthesize where the models converged
- identify divergence points and what each model uniquely contributed
- recommend a concrete action sequence for the next version
- if comparison with previous rounds is possible, include "What this round added vs. the last"

**Modals:** one per model, with the full response in `white-space: pre-wrap`.

**Grid:** 1 model -> 1 column; 2 -> 2 columns; 3+ -> 3 columns, capped at 3.

**Output filename:** `~/Downloads/<project-slug>_AI_Reviews_<YYYY-MM-DD>.html`
Example: `UV_AI_Reviews_2026-03-28.html`

### 6. Confirm Delivery

After saving the HTML, tell the user the full generated file path.
