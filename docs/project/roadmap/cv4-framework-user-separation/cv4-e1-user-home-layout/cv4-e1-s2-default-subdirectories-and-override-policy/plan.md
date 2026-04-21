[< CV4.E1 User Home Layout](../index.md)

# CV4.E1.S2 — Plan: Define default subdirectories and override policy

## What and Why

CV4.E1.S1 defines how the active user home is resolved. This story builds on
that contract and defines what happens *inside* the user home by default, and
which of those paths may be overridden.

The goal is to avoid two failure modes:
- every feature invents its own path rules independently
- every path becomes mandatory configuration, making the system noisy and brittle

The direction is:
- keep `MIRROR_HOME` as the primary contract
- derive sensible defaults from it
- keep `DB_PATH` only as a compatibility bridge, not a long-term primary contract
- allow targeted overrides only where they are genuinely useful

---

## Proposed Defaults

Given:

```env
MIRROR_HOME=~/.mirror/<user>
```

The default internal layout is:

```text
~/.mirror/<user>/
  identity/
  memory.db
  backups/
  exports/
  exports/transcripts/
```

Derived defaults:
- `identity/` → fixed, not user-configurable
- `memory.db` → fixed canonical default, with `DB_PATH` retained only as a compatibility bridge during migration
- `backups/` → default only, overridable
- `exports/` → default only, overridable
- `exports/transcripts/` → default only, overridable and inheriting from the export root when only the export root is overridden

---

## Override Policy

### Fixed contract paths

These should be treated as part of the canonical user-home contract:
- `identity/`
- `memory.db`

They should not require routine configuration for normal use.

### Overridable paths

These should default from `MIRROR_HOME`, but support explicit override:
- backup destination
- export destination
- transcript export destination

This matches the actual use case:
- many users will accept local defaults
- some users will want Dropbox/iCloud/Obsidian or another external path

### Configuration direction

The likely env-var direction is:

```env
MIRROR_HOME=~/.mirror/<user>
EXPORT_DIR=~/.mirror/<user>/exports
TRANSCRIPT_EXPORT_AUTOMATIC=false
TRANSCRIPT_EXPORT_DIR=~/.mirror/<user>/exports/transcripts
```

Likely companion override variables also include a backup destination override.
This story should decide the policy before final naming is locked everywhere.

Transcript export inheritance rule:
1. if `TRANSCRIPT_EXPORT_DIR` is set, use it
2. else if `EXPORT_DIR` is set, use `<EXPORT_DIR>/transcripts`
3. else use `~/.mirror/<user>/exports/transcripts`

---

## Questions This Story Should Settle

1. How should backup destination naming align with the existing `DB_BACKUP_PATH` compatibility surface?
2. Should backup and export overrides remain first-class env vars? (Direction: yes)
3. Should transcript export inherit from `exports/` when only one export override is set? (Direction: yes)
4. Should override variables allow paths outside the user home? (Direction: yes)
5. What documentation language distinguishes canonical defaults from compatibility overrides?

---

## Recommended Direction

- `MIRROR_HOME` is primary
- defaults are derived from `MIRROR_HOME`
- `DB_PATH` is compatibility-only
- override only where there is a strong user need
- paths outside the user home are allowed for exports and backups
- transcript export inherits from the export root unless explicitly overridden
- fixed contract paths should stay few in number

This keeps the system ergonomic for the common case while preserving flexibility
for operational workflows.

---

## Deliverable

This story should produce planning/docs that define:
- the default in-home subdirectory layout
- which paths are fixed vs. overridable
- the override-policy principle that later implementation stories will follow

Implementation belongs to later CV4 epics and stories.

---

## Risks and Design Concerns

### 1. Too many path env vars
If every path gets its own required setting, the system becomes configuration-heavy.

### 2. Hidden compatibility drag
If old variables like `DB_PATH` stay first-class forever, `MIRROR_HOME` stops being
meaningful as the primary contract.

### 3. Confusing exports with runtime truth
Exports and backups are operational artifacts, not runtime truth. `memory.db` is.

### 4. Implicit transcript path behavior
Transcript export should be explicit enough that users understand where files go,
especially when automatic export is enabled.

---

## Follow-on Work Enabled

Once S2 is accepted, later implementation stories can define exact variable names
and behavior for:
- backup/export path overrides
- transcript export configuration
- compatibility handling for current path variables
