# Data model

> Replace this template with the actual data model of the extension.

For each table the extension owns, document:

- **Table name.** Full name with prefix (`ext_<id>_*`).
- **Purpose.** One paragraph: what this table represents.
- **Columns.** Name, type, nullability, default, constraints, description.
- **Primary key.** Composite or single.
- **Indices.** Name, columns, why this index exists (which query it serves).
- **Foreign keys.** To other tables in the extension, or to core tables.
  Note: core does not enforce FKs across the extension boundary; treat
  cross-boundary references as conventions.
- **Notes.** Anything that surprised you while designing it.

End the document with a section on **invariants**: facts that must always
hold across the schema (e.g., "every transaction has a non-null
`account_id` pointing to an existing account"). Invariants are the
extension author's contract with future readers.
