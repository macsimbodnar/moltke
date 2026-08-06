id:         S018
goal:       plan_done and append-only immutability survives a commit
accepts:    modifying a plan_done file or rewriting earlier bytes of decisions.md or worklog.md is still a violation after the tampering is committed; additions to plan_done stay legal; repositories with no git history still abstain; INV-7's wording in specs.md is restated against the committed baseline with the old 'session start' wording marked superseded in this same commit; red observed by committing the tampering from the audit report's own reproduction
touches:    bin/moltke.py inv_7_done_immutable and inv_8_append_only; adocs/specs.md INV-7; tests/test_s003_invariants.py; tests/test_s004_invariants.py
excludes:   adding these checks to --post-write, which CHEAP_CHECKS deliberately excludes for cost; detecting a file created and deleted within one audit
decisions:
closes:     2026-08-06_adversarial-F04, 2026-08-06_adversarial-F12
blocks:
paused_by:
done:
