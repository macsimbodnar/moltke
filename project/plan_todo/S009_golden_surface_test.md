id:         S009
goal:       golden test over the moltke CLI surface, plus the AGENTS.md identity test
accepts:    golden test fails when a moltke.py command or flag is added, renamed, or removed, and stays failing until MANUAL and the specs rows are updated in the same commit; a test asserts AGENTS.md and templates/AGENTS.md are byte-identical
touches:    tests/
decisions:  DEC-010, DEC-012
done:
