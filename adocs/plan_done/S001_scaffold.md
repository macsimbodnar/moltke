id:         S001
goal:       scaffold this repository against its own conventions, seed decisions DEC-001 to DEC-012
accepts:    project/ matches the AGENTS.md §2 file map; .workflow.json parses with schema 1, enabled true, surface_guard "cli"; CLAUDE.md contains @AGENTS.md; decisions.md holds DEC-001..DEC-012, ids unique, newest first; plan.md orders S001..S011 with a step file per id; step ids unique across the three plan directories; specs.md opens with a prime directive and numbered invariants
touches:    repo root, project/
excludes:   all code and tooling (S002+), hooks (S005), templates/ and the Cursor pointer (S006, needs live-docs check first), plugin manifest (S010), README and MANUAL (S011)
decisions:  DEC-003, DEC-004, DEC-005, DEC-008, DEC-009, DEC-012
done:       2026-08-01 scaffolded by hand pre-tooling; manual checks green (testing.md S001 rows); README and MANUAL checked — both absent by plan (S011)
