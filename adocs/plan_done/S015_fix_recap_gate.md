id:         S015
goal:       Stop's recap gate fires in a live session
accepts:    with --log-prompt having run first, --stop still blocks when source changed and no recap heading follows the last logged prompt; a recap heading unblocks; every TestStop fixture logs a prompt before stopping, so the test states the live precondition; red observed against the current implementation
touches:    bin/moltke.py mode_stop; tests/test_s005_hooks.py TestStop
excludes:   changing the recap heading convention itself; any worklog parsing beyond heading detection
decisions:
closes:     2026-08-06_adversarial-F01
blocks:
paused_by:
done:      2026-08-06: recap gate reads headings, not worklog growth; abstains before the first commit; recap wins when a heading reads as both. 6 tests in test_s005_hooks.py, all observed red, every TestStop fixture now logs a prompt first. Suite 120 OK, --validate green. README test count 116 to 120; MANUAL entry rewritten from 'one hook enforces less' to the two live consequences, earlier-turn recap and pre-commit abstain. F01 stays planned until S027 re-runs the audit; inert in live sessions until 0.3.0 is installed.
