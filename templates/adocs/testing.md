# Testing ledger

Acceptance criteria with their covering tests. Rows are added with the feature,
never after, and not edited once written — append only is the rule for writing
rows, not a promise that a row stays. `--step done` drops a row when one
completion prunes the `plan.md` entry of every step that row names, on the same
newest-5-done window as the plan; `plan_done/` and git keep the history. Rows
are voluntary documentation: `test_command` is what gates a green suite.

| Step | Criterion | Covering test | Result |
|---|---|---|---|
