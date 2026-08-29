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

1. S164  init wires the ruleset into an existing CLAUDE.md (2026-08-29 audit, medium)
2. S165  init's Detect table covers a moltke AGENTS.md without adocs/
3. S166  init records adoption under the next free DEC id
4. S167  MANUAL and the ruleset agree on the merge-collision renumber
5. S168  the audit id grammar can express its own re-run suffix
6. S169  MANUAL discloses that an install ships this repository whole
7. S170  README's Ship order commits the bump before the push

## Done recently

Last five; the full record is `plan_done/`.

- S158  the reviewer fence knows when a run ended
- S159  the step skill stops pointing a drive-by fix at the recap
- S160  replace the enforcement product with the v1 rules product
- S162  keep the 0.x -> 1.0 migration prompt in the repo's memory
- S161  1.0.0 released: master carries the v1 tree, the config root serves it
