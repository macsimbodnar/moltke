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

## 2026-08-01 recap S005

- Step: S005 hooks wiring.
- Changed: bin/moltke.py (mode_session_start, mode_log_prompt, mode_pre_write, mode_post_write, mode_stop, derived_next/status_next, 3-block stop cap); hooks/hooks.json (five events, ${CLAUDE_PLUGIN_ROOT}); tests/test_s005_hooks.py (16 tests); fixtures gained status.md.
- Live-docs deviations recorded in specs: UserPromptSubmit exit 2 erases the prompt (log fails open); SessionStart context via hookSpecificOutput.additionalContext; no documented Stop cap (self-imposed cap of 3, state in .git/moltke_stop_state.json).
- Red observed: 8 failures + 2 errors before implementation; 49/49 green after. Dogfood --validate passes.
- README/MANUAL: checked, absent by plan (S011).
- Commit: 3f9b649

## 2026-08-01T17:30+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S006

- Step: S006 init skill and templates tree.
- Changed: bin/moltke.py (mode_scaffold, mode_decline, scaffold_root, declined, plan_text); skills/init/SKILL.md; templates/ (AGENTS.md copy, CLAUDE.md, cursor_rules, moltke.json, project/*.md, step_template.md, audit_report_template.md); tests/test_s006_scaffold.py (12 tests).
- Red observed: 6 failures + 3 errors before implementation; 61/61 green after.
- Defect found by end-to-end scaffold of a throwaway repo (not by unit tests): commented-out example step in the plan template produced a phantom next step S001, a false stale-status.md report, and a Stop block on the first turn of a fresh repo. Regression test written first (red: "'stale' unexpectedly found in ... derived next step: s001"), then plan_text() strips comments and fenced blocks in derived_next and INV-3.
- Trivial in-scope fix: AGENTS.md 8 carried a live DEC-013 cross-reference that would have shipped into other repos; reworded before copying to templates. Caught by the genericity test.
- DEC-017 (setup modes exempt from INV-11, --decline added to the surface) and DEC-018 (thin Cursor pointer; Cursor reads AGENTS.md natively) recorded.
- README/MANUAL: checked, absent by plan (S011).
- Commits: d93673c (decisions + ruleset fix), c52f044 (S006).

## 2026-08-01T18:15+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S007

- Step: S007 step skill and lifecycle operations.
- Changed: bin/moltke.py (field_value, locate_step, next_step_id, write_step, append_to_plan, set_field, step_new/start/block/done/status, mode_step); skills/step/SKILL.md; tests/test_s007_step.py (19 tests).
- Red observed: 16 failures + 1 error before implementation; 82/82 green after.
- Two latent defects found and fixed red-first: (1) unfilled `paused_by: <!-- ... -->` placeholder counted as a real pause, hiding a second active step from INV-1 (red: "0 != 1 : moltke: all checks pass"); (2) INV-4 treated a completed child's `blocks:` as live, which would block the parent forever. Both recorded in specs.
- Also fixed: `set_field` silently did nothing when a step file lacked the key; a refusal echoed a raw field value ("complete S004  # 2026-08-01 first"). One test re-targeted to exercise the blocks gate in isolation, with a new test added for the paused gate (both gates now covered, coverage strengthened not reduced).
- Dogfood: full lifecycle (new, start, block, refused parent completion, refused child completion without testing row, completion, status) verified on a throwaway repo; then S007 itself completed with `--step done` and status.md regenerated by `--step status`, Parked list preserved.
- Observation, not a defect: with a step in progress, status shows it as both "In progress" and "Next", which is exactly the AGENTS.md 1 derivation (first step in plan order not in plan_done).
- README/MANUAL: checked, absent by plan (S011).
- Commit: see below.

## 2026-08-01T19:00+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S008

- Step: S008 adversarial_reviewer subagent and audit skill.
- Changed: bin/moltke.py (strip_guidance, finding_references, report_findings, inv_10 id-prefix check, reviewer fence in mode_pre_write, audit_new/audit_list/mode_audit); agents/adversarial_reviewer.md; skills/audit/SKILL.md; templates/audit_report_template.md restructured so the format example is fenced; tests/test_s008_audit.py (12 tests) + 1 regression test in test_s006_scaffold.py.
- Red observed: 9 failures + 1 error before implementation; 95/95 green after.
- Live-docs check: subagent frontmatter supports tools/disallowedTools but no path restriction, so the "writes only to project/audit/" rule is enforced by the PreToolUse hook via agent_type. Recorded in specs.
- Defect found by dogfooding: scaffolded decisions.md template example DEC-001 collided with a user's first real DEC-001 (false INV-9 duplicate). Fourth instance of guidance-parsed-as-data; consolidated into strip_guidance used by every scanner, rule recorded in specs. Red observed first.
- Not done here: the reviewer cannot actually be spawned until the plugin is installed (S010); no audit report was created in this repo, because a report nobody ran would be fabricated evidence.
- README/MANUAL: checked, absent by plan (S011).
- Commit: see below.

## 2026-08-01T19:45+02:00 prompt (hand-logged)

> next

## 2026-08-01 recap S009

- Step: S009 golden surface test.
- Changed: bin/moltke.py (extracted build_parser so the surface is introspectable); tests/test_s009_surface.py (5 tests); tests/golden/cli_surface.txt.
- Red observed by tampering, twice: added flag `--purge` and added `--step abandon`; each failed both the golden and the documentation check, output recorded in testing.md; both reverted and suite green after.
- Tightened during the step: the documentation check originally matched a bare word anywhere in the file, so `--step new` was satisfied by the word "new" in prose. Now an operation counts only on a line that also names its mode.
- Known gap, recorded not hidden: the MANUAL half is skipped until MANUAL.md exists; the S011 step file carries the instruction to confirm it stops skipping and actually bites.
- DEC-012 identity: verified covered by test_s006_scaffold.py, not duplicated; a tripwire asserts the guard still exists.
- README/MANUAL: checked, absent by plan (S011).
- Commit: see below.
