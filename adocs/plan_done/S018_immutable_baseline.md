id:         S018
goal:       plan_done and append-only immutability survives a commit
accepts:    modifying a plan_done file or rewriting earlier bytes of decisions.md is still a violation after the tampering is committed; additions to plan_done stay legal; repositories with no git history still abstain; INV-7's wording in specs.md is restated against the committed baseline with the old 'session start' wording marked superseded in this same commit; red observed by committing the tampering from the audit report's own reproduction
touches:    bin/moltke.py inv_7_done_immutable and inv_8_append_only; adocs/specs.md INV-7; tests/test_s003_invariants.py; tests/test_s004_invariants.py
excludes:   adding these checks to --post-write, which CHEAP_CHECKS deliberately excludes for cost; detecting a file created and deleted within one audit; worklog.md, which DEC-025 removed from INV-8 in S030 — this step must run after it
decisions:  DEC-025
closes:     2026-08-06_adversarial-F04, 2026-08-06_adversarial-F12
blocks:
paused_by:
done:      2026-08-06: INV-7 and INV-8 each check two baselines, HEAD for the uncommitted window and git log for everything committed; --no-renames keeps a move in as an addition, which is what keeps the S013 rename legal. INV-7's specs wording restated with the session-start sentence marked superseded (F12). 6 tests, red observed as 'moltke: all checks pass' after committing the tampering. Suite 138 OK, --validate green including this repo's own 18-entry plan_done history. README test count 132 to 138; MANUAL immutability entry rewritten to say history is read too, with the two known limits and the fact that neither check reverts anything.
