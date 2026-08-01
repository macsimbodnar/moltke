# Testing ledger

Acceptance criteria with their covering tests. Rows are added with the feature,
never after. Append only.

| Step | Criterion | Covering test | Result |
|---|---|---|---|
| S001 | `project/` matches the AGENTS.md §2 file map; `CLAUDE.md` contains `@AGENTS.md` | manual shell check (S001, pre-suite; automated by `--validate` from S002) | pass 2026-08-01 |
| S001 | `.workflow.json` parses; `schema` 1, `enabled` true, `surface_guard` `cli` | manual `json.load` check (S001) | pass 2026-08-01 |
| S001 | step ids unique across plan dirs; every `plan_todo/` and `plan_current/` file listed in `plan.md` | manual check (S001; automated by INV-3/INV-6 tests in S003) | pass 2026-08-01 |
| S001 | `decisions.md` holds exactly DEC-012..DEC-001, unique, newest first | manual check (S001; automated by INV-9 test in S004) | pass 2026-08-01 |
