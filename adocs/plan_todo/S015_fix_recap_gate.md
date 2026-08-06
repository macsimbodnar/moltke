id:         S015
goal:       Stop's recap gate fires in a live session
accepts:    with --log-prompt having run first, --stop still blocks when source changed and no recap heading follows the last logged prompt; a recap heading unblocks; every TestStop fixture logs a prompt before stopping, so the test states the live precondition; red observed against the current implementation
touches:    bin/moltke.py mode_stop; tests/test_s005_hooks.py TestStop
excludes:   changing the recap heading convention itself; any worklog parsing beyond heading detection
decisions:
closes:     2026-08-06_adversarial-F01
blocks:
paused_by:
done:
