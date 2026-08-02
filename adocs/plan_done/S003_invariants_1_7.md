id:         S003
goal:       invariants 1 to 7, red-first, one test each
accepts:    each of INV-1..INV-7 has a test observed failing against a broken fixture before the implementation, with the failure output recorded; one testing.md row per invariant
touches:    bin/moltke.py, tests/
excludes:   INV-8..INV-10 (S004)
decisions:  DEC-007, DEC-008
done:       2026-08-01 suite green 24/24; red observed against the empty registry (9 failures, 0 != 1); one S002 test re-targeted to the plan-tree fixture (deliberate strengthening, noted in recap); README and MANUAL checked, absent by plan (S011)
