# Plan

moltke 1.0: the document-driven workflow shipped as rules, not enforcement
(DEC-062). The plugin is markdown only — `/moltke:init` interviews the user and
records per-project rules in `AGENTS.md` (DEC-063), the plan lives as step
files moved by hand between three directories, and a slim `/moltke:audit`
keeps the adversarial reviewer. The 0.x enforcement product — hooks, checker,
watchers, fences — is deleted; its record is `plan_done/` and git history.
Spec: `adocs/specs.md`.

Order lives here and nowhere else. Step detail lives in the step files.

## Open

Nothing open past the 2026-08-29 audit steps; the next id is S171.

## Done recently

Last five; the full record is `plan_done/`.

- S166  init records adoption under the next free DEC id
- S167  MANUAL and the ruleset agree on the merge-collision renumber
- S168  the audit id grammar can express its own re-run suffix
- S169  MANUAL discloses that an install ships this repository whole
- S170  README's Ship order commits the bump before the push
