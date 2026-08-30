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

Nothing open. The 2026-08-29 .3 re-run's round (S174-S179) is done; the
user decides whether it ships as 1.1.1 or waits. The next id is S180.

## Done recently

Last five; the full record is `plan_done/`.

- S175  the repair branch reconciles view files it creates
- S176  first-plan ids use highest-ever-allocated
- S177  the Ship order includes the release tag
- S178  rules Drop points catalog topics at their none option
- S179  the 0.x archive branch is lost, the claim withdrawn (DEC-070)
