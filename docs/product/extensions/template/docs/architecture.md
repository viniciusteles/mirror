# Architecture

> Replace this template with the actual architecture of the extension.

Topics to cover:

- **Internal modules.** What files exist under `src/`, and what each one is
  responsible for. A small diagram helps.
- **Data flow.** For each user-facing capability, trace the path from input
  (CLI args or Mirror Mode call) through the layers (parsers, store, reports)
  to output.
- **Key decisions.** Choices that future readers might question. Why this
  schema, why this parser registry, why this LLM prompt shape, why this
  embedding strategy. Link to the user story that prompted each decision.
- **Open extensions points.** Places where the extension is designed to be
  extended (e.g., a parser registry for new file formats). Document the
  contract.
- **What is intentionally simple.** Capabilities you considered and rejected,
  with reasons. Reduces the chance someone re-opens the question without
  context.

Keep it readable for a future maintainer who has never seen the code.
