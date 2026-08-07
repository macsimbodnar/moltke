id:         S041
goal:       the reviewer fence normalises paths before matching
accepts:    a relative path is resolved against the repository root before rel.parts is inspected, and any path escaping the root is refused rather than allowed; 'tests/../bin/moltke.py' is blocked for the reviewer as 'bin/moltke.py' already is; absolute paths behave exactly as today; the plan_done and step-file rules get the same normalised path, since they read the same rel; red observed with the finding's table, where the relative escape is allowed and the absolute equivalent is blocked
touches:    bin/moltke.py mode_pre_write, reviewer_may_write; tests/test_s008_audit.py; tests/test_s005_hooks.py TestPreWrite
excludes:   following symlinks, which is a different question; the Bash gap, which DEC-022 accepted
decisions:
closes:     2026-08-07_adversarial-F10
blocks:
paused_by:
done:      2026-08-07: --pre-write resolves the path before any rule reads it, so a relative escape through an allowed directory is judged by where it lands; the reviewer fence, the plan_done rule, and the step-file rule share that one rel and are all fixed together. 6 tests, red observed on two of the three rules. Suite 223 OK, --validate green, and the finding's table re-measured. README test count 217 to 223; MANUAL's fence entry now states that paths are resolved first and that anything outside the repository is unpoliced. Acceptance narrowed and recorded: escapes that leave the repository stay unpoliced, which is the existing deliberate boundary.
