id:         S009
goal:       golden test over the moltke CLI surface, plus the AGENTS.md identity test
accepts:    golden test fails when a moltke.py command or flag is added, renamed, or removed, and stays failing until MANUAL and the specs rows are updated in the same commit; the AGENTS.md identity test already landed in S006 (test_s006_scaffold.py TestTemplatesAreGeneric) — verify it covers DEC-012 and do not duplicate it
touches:    tests/
decisions:  DEC-010, DEC-012
done:
