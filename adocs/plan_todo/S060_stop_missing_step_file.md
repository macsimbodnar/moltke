id:         S060
goal:       --stop enforces instead of crashing when a plan_done/ arrival is not on disk
accepts:    the stamp gate skips a porcelain entry that is not an existing file before parse_step_file reads it, so the AD, RD, and collapsed `?? adocs/plan_done/` shapes each exit 2 or 0 and never 1; mode_stop and mode_post_write gain the OSError refusal mode_step got in S052, so an unreadable tree names the path instead of raising; mode_stop reads porcelain with -uall like worktree_state, or handles the collapsed directory entry explicitly, so both gates and the audit baseline read one shape; the problems collected before the crash are printed in every case, verified with a fixture holding an INV-3 violation, a stale status.md, and the stamp complaint together; red observed with the traceback and the empty stderr on all three shapes
touches:    bin/moltke.py mode_stop stamp gate, mode_post_write; tests/test_s005_hooks.py
excludes:   changing which statuses count as an arrival, which S050 settled; the pre-write fence on plan_done/, which is what makes the mv remedy the only way out
decisions:
closes:     2026-08-08_adversarial-F01
blocks:
paused_by:
done:
