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

## 2026-08-01T15:20+02:00 prompts (hand-logged as a batch)

> What is the next step? All defered decisions or anything that i should decide now let's solce it in iteractive way now

> I will handle github configuration by myslef. You just create commits and nothing else. Untill new orders

> What would be most efficient way to handle decisions? Appending is faster but then you need to read the whole file and consume more tokens. if adding on top is something that will not require to read the whole file increasing the context the nlet's put on top, if not then on bottom

> bottom

## 2026-08-01 recap decisions ordering

- Not a step; rules and decisions turn.
- DEC-013: decisions.md newest last; AGENTS.md §2/§8 amended; DEC-001..DEC-012 reordered oldest first (one-time exception authorized by DEC-013); S004 reconcile clause dropped; superseding testing.md row appended.
- DEC-014: GitHub configuration is Max's own; agent commits only, until new orders.
- Commit: e8084d3

## 2026-08-01T15:45+02:00 prompt (hand-logged)

> ok, before proceeding i want to rename the project, repository and commands. The new name of the project is moltke (Moltke commanded armies he could not see by writing orders that survived his absence. Same problem, smaller scale.)

## 2026-08-01 recap moltke rename

- Not a step; naming decision turn. Scope question answered by Max: full rename.
- DEC-015: plugin/repo `moltke`, CLI `bin/moltke.py`, marker `.moltke.json`, skills init/step/audit under /moltke:.
- Renamed: `.workflow.json` → `.moltke.json`; step files S002/S006/S007 short names; specs, AGENTS.md, plan, status, plan_todo step files updated. Immutable history keeps old names, reads through DEC-015.
- Superseding testing.md row appended for the marker.
- GitHub repo rename and local directory rename left to Max (DEC-014).
- Commit: 00da550

## 2026-08-01T16:10+02:00 prompt (hand-logged)

> before proceeding i just want to evaluate if it even makes sense to create this project. For example i found this one https://github.com/SpillwaveSolutions/project-memory and there are many others. Maybe there is one out there that is actually a standard for this so i don't need to reinvent the wheel. Please search online for it and evaluate if i should proceed with the project or not

## 2026-08-01T16:35+02:00 prompt (hand-logged)

> ok i want to proceed. let's proceed

## 2026-08-01 recap S002

- Step: S002 moltke.py skeleton.
- Changed: bin/moltke.py (find_root, load_marker/check_marker, INV-11 gate, --validate with INVARIANT_CHECKS registry, hook-mode stubs for S005); tests/fixtures.py (broken-fixture builders); tests/test_s002_marker.py (12 tests).
- Red observed: stub version exiting 0 everywhere -> 9 of 12 failed ("AssertionError: 0 != 1", "'all checks pass' not found in ''"); the 3 passing were INV-11 gate tests whose non-vacuity partners were among the failures. Then implemented; 12/12 green. Dogfood: `python3 bin/moltke.py --validate` passes on this repo.
- Flagged: INV-11 vs --scaffold tension (scaffold must run unmarked); routed to S006 step file and status parked.
- README/MANUAL: checked, absent by plan (S011).
- Commit: 2a50f1d

## 2026-08-01 recap S003

- Step: S003 invariants 1-7.
- Changed: bin/moltke.py (step parsing, plan_steps, inv_1..inv_7 registered); tests/fixtures.py (step_file, workflow_repo); tests/test_s003_invariants.py (12 tests).
- Red observed: empty registry -> 9 failures ("AssertionError: 0 != 1"), then implemented, 24/24 green. Dogfood --validate passes on this repo.
- INV-7 interpretation recorded in specs (git HEAD baseline, additions legal, abstain without git). INV-3 strengthened: missing plan.md in an enabled repo is a violation; re-targeted test_valid_marker_passes from bare marker to plan tree (strengthening, not weakening).
- README/MANUAL: checked, absent by plan (S011).
- Commit: 70f7e2b

## 2026-08-01 recap S004

- Step: S004 invariants 8-10.
- Changed: bin/moltke.py (inv_8 byte-prefix vs git HEAD, inv_9 unique DEC ids, inv_10 finding statuses and open-finding references); tests/fixtures.py (decisions/worklog in workflow_repo, audit_report helper); tests/test_s004_invariants.py (9 tests).
- Red observed: 6 failures ("AssertionError: 0 != 1") before implementation; 33/33 green after. Dogfood --validate passes on this repo.
- INV-10 fixed the finding format ahead of S008 (### <report>-F<nn> + Status: line); noted in specs and the S008 step file.
- README/MANUAL: checked, absent by plan (S011).
- Commit: 21b27d0
