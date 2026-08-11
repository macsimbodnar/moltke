id:         S126
goal:       testing.md rows pruned with the plan window
accepts:    acceptance criteria, testable
touches:    areas of the codebase
excludes:   explicitly out of scope
decisions:
closes:
blocks:
paused_by:
done:      2026-08-11: testing.md rows are pruned with the plan window (DEC-048). A row leaves only when every step id it references was just pruned from plan.md; open work and the kept last-5 stay, git keeps every row, and a failed prune is not a failed completion because the ledger is voluntary. Suite 396 OK, --validate green. Docs already describe the voluntary ledger; no further change.
author:    Maksym Bodnar
