id:         S054
goal:       INV-8's enforced rule and its stated rule agree
accepts:    either a decision inserted mid-file is a violation, or INV-8's wording in specs.md stops saying earlier bytes are unchanged and says what the line-subsequence rule actually guarantees, with the fabricated-entry case named; MANUAL stops describing the pre-S046 first-commit baseline; whichever is chosen, DEC-026's repair-clears property and DEC-028's high-water mark still hold, and the choice is recorded because tightening to a prefix rule is what DEC-028 measured as unsatisfiable after a repair
touches:    adocs/specs.md INV-8; MANUAL.md; possibly bin/moltke.py inv_8_append_only; tests/test_s004_invariants.py; adocs/decisions.md
excludes:   reverting to the numstat rule, which DEC-026 rejected for having no terminal state
decisions:
closes:     2026-08-07_adversarial.2-F07
blocks:
paused_by:
done:
