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

1. S171  release 1.1.0, tagged (in progress)

## Done recently

Last five; the full record is `plan_done/`.

- S168  the audit id grammar can express its own re-run suffix
- S169  MANUAL discloses that an install ships this repository whole
- S170  README's Ship order commits the bump before the push
- S172  re-running init repairs unwired entry points
- S173  init's first-plan step respects kept files
