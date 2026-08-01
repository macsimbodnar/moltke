# Worklog

Append only. Forensic history for humans, never a context source (DEC-011).
Mechanical prompt logging starts when hooks land (S005); until then entries are
appended by hand.

## 2026-08-01T14:54+02:00 prompt

> read bootstrap.md and AGENTS.md, then work S001 from section 8

## 2026-08-01 recap S001

- Step: S001 scaffold, worked by hand per specs (pre-tooling).
- Changed: `.workflow.json`, `CLAUDE.md`, `.gitignore`; `bootstrap.md` moved to `project/specs.md` and restructured (prime directive, INV-1..INV-12); `project/` tree per AGENTS.md §2; DEC-001..DEC-012 seeded newest first; plan.md ordering S001..S011 with one step file each; S001 completed into `plan_done/`.
- Tests: none yet (suite arrives S002). Manual invariant checks run and recorded in testing.md; first run caught missing `plan_done/`, fixed, re-run green.
- README/MANUAL: checked — both absent by plan (S011).
- Flagged: INV-8 append-only bytes vs decisions.md newest-first ordering conflict, routed to S004.
- Commits: 21a8226 (scaffold), 2fcbb94 (untrack stray `.claude/` temp file swept in by `git add -A`).
