id:         S041
goal:       the reviewer fence normalises paths before matching
accepts:    a relative path is resolved against the repository root before rel.parts is inspected, and any path escaping the root is refused rather than allowed; 'tests/../bin/moltke.py' is blocked for the reviewer as 'bin/moltke.py' already is; absolute paths behave exactly as today; the plan_done and step-file rules get the same normalised path, since they read the same rel; red observed with the finding's table, where the relative escape is allowed and the absolute equivalent is blocked
touches:    bin/moltke.py mode_pre_write, reviewer_may_write; tests/test_s008_audit.py; tests/test_s005_hooks.py TestPreWrite
excludes:   following symlinks, which is a different question; the Bash gap, which DEC-022 accepted
decisions:
closes:     2026-08-07_adversarial-F10
blocks:
paused_by:
done:
