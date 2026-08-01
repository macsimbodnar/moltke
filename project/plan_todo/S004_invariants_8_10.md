id:         S004
goal:       invariants 8 to 10
accepts:    each of INV-8..INV-10 has a test observed failing against a broken fixture before the implementation, with the failure output recorded; one testing.md row per invariant; INV-8 semantics reconciled with decisions.md being "append only, newest first" (a new entry at the top shifts earlier bytes — define what "append only" checks and record the definition, decisions.md entry if it amends INV-8)
touches:    bin/workflow_check.py, tests/
decisions:  DEC-011
done:
