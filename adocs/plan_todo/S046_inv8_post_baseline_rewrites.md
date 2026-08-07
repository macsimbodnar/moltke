id:         S046
goal:       INV-8 catches a committed rewrite of text appended after the first commit
accepts:    a rewrite of post-baseline content is reported after it is committed, not only while it is uncommitted, and a repair still clears it — both halves together, since DEC-027 shows either one alone is easy; the measured probe in DEC-027 is the fixture, where the committed post-baseline rewrite exits 0 today; whatever rule is chosen is stated in specs with the case it cannot see, because a rule that claims to see everything is the failure mode DEC-027 was written about
touches:    bin/moltke.py inv_8_append_only; tests/test_s004_invariants.py; adocs/specs.md; MANUAL.md
excludes:   history rewriting; reverting to the --numstat rule, which DEC-026 rejected for having no terminal state
decisions:  DEC-026, DEC-027
closes:
blocks:
paused_by:
done:
