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

The 2026-08-29 .3 re-run's round, unstarted — the user decides whether it
ships as 1.1.1 or waits:

1. S175  the repair branch reconciles view files it creates
2. S176  first-plan ids use highest-ever-allocated
3. S177  the Ship order includes the release tag
4. S178  rules Drop points catalog topics at their none option
5. S179  the 0.x archive branch exists somewhere real, or the claim goes

## Done recently

Last five; the full record is `plan_done/`.

- S170  README's Ship order commits the bump before the push
- S172  re-running init repairs unwired entry points
- S173  init's first-plan step respects kept files
- S171  1.1.0 released and tagged
- S174  init's status step stops contradicting INV-19
