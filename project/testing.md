# Testing ledger

Acceptance criteria with their covering tests. Rows are added with the feature,
never after. Append only.

| Step | Criterion | Covering test | Result |
|---|---|---|---|
| S001 | `project/` matches the AGENTS.md §2 file map; `CLAUDE.md` contains `@AGENTS.md` | manual shell check (S001, pre-suite; automated by `--validate` from S002) | pass 2026-08-01 |
| S001 | `.workflow.json` parses; `schema` 1, `enabled` true, `surface_guard` `cli` | manual `json.load` check (S001) | pass 2026-08-01 |
| S001 | step ids unique across plan dirs; every `plan_todo/` and `plan_current/` file listed in `plan.md` | manual check (S001; automated by INV-3/INV-6 tests in S003) | pass 2026-08-01 |
| S001 | `decisions.md` holds exactly DEC-012..DEC-001, unique, newest first | manual check (S001; automated by INV-9 test in S004) | pass 2026-08-01 |
| S001 | `decisions.md` ordered oldest first, DEC-001..newest at bottom, ids unique (DEC-013; supersedes the newest-first row above) | manual check (automated by INV-9 test in S004) | pass 2026-08-01 |
| S001 | `.moltke.json` parses; `schema` 1, `enabled` true, `surface_guard` `cli` (DEC-015; supersedes the `.workflow.json` row above) | manual `json.load` check | pass 2026-08-01 |
| S002 | INV-11: every mode exits 0 in an unmarked repo | tests/test_s002_marker.py TestInv11MarkerGate.test_every_mode_exits_0_without_marker | pass 2026-08-01 |
| S002 | INV-11: every mode exits 0 when `enabled` is false, even alongside other marker errors | TestInv11MarkerGate.test_every_mode_exits_0_when_disabled, test_disabled_beats_other_marker_errors | pass 2026-08-01 |
| S002 | marker is found from any subdirectory of the repo | TestInv11MarkerGate.test_marker_found_from_subdirectory | pass 2026-08-01 |
| S002 | `--validate` exits 1 and names every marker violation: unreadable JSON, non-object, schema, enabled, limits, surface_guard; all reported, not just the first | tests/test_s002_marker.py TestValidateMarker (red observed against the S002 stub: 9 failures, `0 != 1`; output in worklog recap) | pass 2026-08-01 |
| S002 | `--validate` exits 0 with "all checks pass" on a valid fixture and on this repository | TestValidateMarker.test_valid_marker_passes + `python3 bin/moltke.py --validate` here | pass 2026-08-01 |
| S003 | INV-1: more than `plan_active_max` non-paused steps in `plan_current/` is a violation; paused steps do not count | test_s003_invariants.py test_inv1_too_many_non_paused_steps, test_inv1_paused_steps_do_not_count | pass 2026-08-01 |
| S003 | INV-2: stack depth over `plan_stack_max` is a violation | test_inv2_stack_depth_exceeded | pass 2026-08-01 |
| S003 | INV-3: a step file in `plan_todo/` or `plan_current/` absent from `plan.md` is a violation; missing `plan.md` in an enabled repo too | test_inv3_step_missing_from_plan | pass 2026-08-01 |
| S003 | INV-4: a `plan_done/` step still named in another step's `blocks:` is a violation | test_inv4_done_step_still_blocking | pass 2026-08-01 |
| S003 | INV-5: a done step without a `done:` stamp or without a `testing.md` row is a violation | test_inv5_done_step_without_stamp, test_inv5_done_step_without_testing_row | pass 2026-08-01 |
| S003 | INV-6: duplicate step ids across the three plan directories are a violation | test_inv6_duplicate_step_id | pass 2026-08-01 |
| S003 | INV-7: modifying or deleting a tracked `plan_done/` file is a violation; adding one is legal; no git baseline means abstain | test_inv7_modified_done_step, test_inv7_deleted_done_step, test_inv7_added_done_step_is_allowed | pass 2026-08-01 |
| S003 | valid tree passes: the base fixture satisfies INV-1..INV-7 (non-vacuity anchor for every broken variant) | test_valid_tree_passes + `python3 bin/moltke.py --validate` here | pass 2026-08-01 |
| S004 | INV-8: rewriting earlier bytes of `decisions.md` or `worklog.md`, or deleting either, is a violation; appending is legal; no git baseline means abstain | test_s004_invariants.py TestAppendOnly (4 tests) | pass 2026-08-01 |
| S004 | INV-9: duplicate `DEC-<nnn>` ids in decisions.md are a violation | TestDecisionIds.test_duplicate_dec_id_fails | pass 2026-08-01 |
| S004 | INV-10: a finding status outside open/planned/closed/accepted is a violation; an open finding with no step `closes:` reference and no decisions.md mention is a violation; referenced or accepted findings pass | TestAuditFindings (4 tests) | pass 2026-08-01 |
| S005 | `--log-prompt` appends the verbatim prompt with a timestamp and never exits non-zero, even on damaged stdin (exit 2 would erase the prompt) | test_s005_hooks.py TestLogPrompt (2 tests) | pass 2026-08-01 |
| S005 | `--pre-write` exits 2 for writes under `plan_done/` and for step files outside the three plan directories; ordinary writes pass; path arrives as argument or hook stdin JSON | TestPreWrite (4 tests) | pass 2026-08-01 |
| S005 | `--session-start` reports the `plan_current/` stack and the derived next step as `additionalContext` JSON, and flags a stale `status.md` | TestSessionStart (2 tests) | pass 2026-08-01 |
| S005 | `--post-write` surfaces cheap-scan violations on stderr with non-blocking semantics; clean repos stay silent | TestPostWrite (2 tests) | pass 2026-08-01 |
| S005 | `--stop` exits 2 on invariant violations, stale status.md, and source changes without a worklog recap; a recap unblocks; after 3 consecutive blocks it allows the stop (no-deadlock cap) | TestStop (6 tests) | pass 2026-08-01 |
