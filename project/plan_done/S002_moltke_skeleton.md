id:         S002
goal:       moltke.py skeleton, marker parsing, --validate mode, broken-fixture test harness
accepts:    Python standard library only; every mode exits 0 immediately when .moltke.json is absent or enabled is false (INV-11); --validate runs every implemented invariant, reports all violations, exits non-zero on any; test harness builds deliberately broken fixture repositories for red-first tests
touches:    bin/moltke.py, tests/
excludes:   individual invariant checks (S003, S004), hook wiring (S005)
decisions:  DEC-005, DEC-006
done:       2026-08-01 suite green 12/12; red observed against the S002 stub (9 failures, recorded in worklog recap); testing.md rows added; README and MANUAL checked, absent by plan (S011)
