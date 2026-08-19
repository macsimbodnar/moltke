id:         S142
goal:       the golden guards hook matchers and mode flags, not just event names
accepts:    dropping the Write|Edit PreToolUse matcher, or repointing the Stop hook at another mode, fails the suite; tests/surface.py declares (event, matcher, mode flag) triples and the golden carries them; red observed first by mutating hooks.json in a scratch copy while the suite was still green
touches:    tests/surface.py, tests/test_s009_surface.py, the refreshed golden
excludes:   changing hooks/hooks.json itself, and guarding hook argument order beyond the mode flag
decisions:
closes:     2026-08-19_adversarial-F02
blocks:
paused_by:
done:
