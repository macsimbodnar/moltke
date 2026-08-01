id:         S002
goal:       workflow_check.py skeleton, marker parsing, --validate mode, broken-fixture test harness
accepts:    Python standard library only; every mode exits 0 immediately when .workflow.json is absent or enabled is false (INV-11); --validate runs every implemented invariant, reports all violations, exits non-zero on any; test harness builds deliberately broken fixture repositories for red-first tests
touches:    bin/workflow_check.py, tests/
excludes:   individual invariant checks (S003, S004), hook wiring (S005)
decisions:  DEC-005, DEC-006
done:
