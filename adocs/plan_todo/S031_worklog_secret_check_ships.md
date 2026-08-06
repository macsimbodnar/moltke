id:         S031
goal:       target repositories inherit the worklog secret check, not just moltke's own suite
accepts:    the S022 shapes move out of tests/test_s022_secrets.py into bin/moltke.py so every marked repository gets them; that test keeps working by importing them, so the detector still has exactly one definition; a decision records where the check runs, since the options differ in blast radius — --validate only, --post-write, or a Stop refusal — and a false positive on someone else's worklog must not be able to deadlock their session; the shapes are reported with a label, a line number, and a truncated match, never the whole value; MANUAL's known-issues note that the check does not travel is removed in the same commit
touches:    bin/moltke.py; tests/test_s022_secrets.py; MANUAL.md; adocs/specs.md
excludes:   redaction at write time, which DEC-024 rejected; entropy or bare-hex heuristics, which false-positive on the commit shas every recap carries; scanning anything beyond the worklog, which is its own question
decisions:  DEC-024
closes:
blocks:
paused_by:
done:
