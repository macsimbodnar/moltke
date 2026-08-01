id:         S004
goal:       invariants 8 to 10
accepts:    each of INV-8..INV-10 has a test observed failing against a broken fixture before the implementation, with the failure output recorded; one testing.md row per invariant; INV-8 is literal byte-append for both worklog.md and decisions.md (DEC-013)
touches:    bin/workflow_check.py, tests/
decisions:  DEC-011, DEC-013
done:
