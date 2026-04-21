[< CV5.E3 Runtime Integration and Validation](../index.md)

# CV5.E3.S1 — Plan — Claude Hook Session Plumbing

## Goal

Use the explicit session ids Claude hooks already receive instead of depending on
singleton state files for mirror routing.

## Design

- extract `session_id` directly in hook scripts where needed
- pass `--session-id` into mirror-state and mirror commands invoked by hooks
- remove unnecessary `current_session` writes from the Claude hook path where
  explicit session ids are already available
- keep session-end behavior tied to the hook payload

## Verification

- hook helper tests for session-scoped mirror state access
- shell-level behavior remains compatible for normal Claude hook invocations
