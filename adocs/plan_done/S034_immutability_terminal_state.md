id:         S034
goal:       a committed immutability violation has a legal way back to green
accepts:    a decisions.md entry is recorded first, choosing among the three options the finding names — accept a repair commit that restores the original bytes, demote a repaired violation to a non-failing note, or read an explicit dated waiver from decisions.md — with the rejected options and their reasons; the chosen option is then implemented so that following the violation message clears it; a genuine unrepaired tampering still fails; the DEC-013 reorder case is used as the worked example, since under today's INV-8 it would make this repository permanently red; red observed by committing tampering, following the prescribed fix, and watching --validate stay at exit 1
touches:    adocs/decisions.md; bin/moltke.py inv_7_done_immutable and inv_8_append_only; adocs/specs.md; tests/test_s003_invariants.py; tests/test_s004_invariants.py; MANUAL.md
excludes:   history rewriting in any form; relaxing the uncommitted-window checks, which are not the defect
decisions:
closes:     2026-08-07_adversarial-F03
blocks:
paused_by:
done:      2026-08-07: INV-7 compares each plan_done file against its add-commit version and INV-8 compares decisions.md against its first-commit version, so a repair commit clears and history is never rewritten. DEC-026 records Max's choice of terminal state; DEC-027 records the mechanism, the two alternatives measured and rejected, and the resulting gap, planned as S046. 5 tests, red observed. Suite 182 OK, --validate green. README test count 177 to 182; MANUAL's immutability entry rewritten to say how to get back to green and to list three limits instead of two.
