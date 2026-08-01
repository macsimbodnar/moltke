id:         S004
goal:       invariants 8 to 10
accepts:    each of INV-8..INV-10 has a test observed failing against a broken fixture before the implementation, with the failure output recorded; one testing.md row per invariant; INV-8 is literal byte-append for both worklog.md and decisions.md (DEC-013)
touches:    bin/moltke.py, tests/
decisions:  DEC-011, DEC-013
done:       2026-08-01 suite green 33/33; red observed (6 failures, 0 != 1) before implementation; testing.md rows added; README and MANUAL checked, absent by plan (S011)
