# User stories

This directory tracks the user stories that drive the extension's development.

## Layout

One file per story, named `US-NN-<slug>.md`. Numbering is local to this
extension (starts at `US-01`). Slug is short, lowercase, dash-separated,
and avoids proper nouns.

## Story file structure

Each story file has three sections:

### 1. Story

The narrative.

- **Como** &lt;papel&gt; (who),
- **quero** &lt;capacidade&gt; (what),
- **para que** &lt;razão&gt; (why).

Plus subsections as needed: **Por que agora**, **Valor de aceitação**,
**Fora do escopo**.

### 2. Plan

The technical plan.

- Files to add or change.
- Sequence of implementation steps (TDD-friendly).
- Decisions herdadas from earlier stories (do not revisit).

### 3. Test Guide

The testing plan.

- Cases by component.
- Edge cases.
- Acceptance criteria (checkboxes).

## Naming

Avoid proper nouns. The story is about the capability, not the brand:

- ✅ `US-04-importar-fatura-cartao`
- ❌ `US-04-importar-fatura-itau`

Banks, vendors, and file formats are parameters of the capability, not its
identity.

## Living documents

Stories are updated as work progresses. When a story ships, mark it
**Done** at the top and date the completion. Do not delete old stories —
they are the record of why the extension looks the way it does.
