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
