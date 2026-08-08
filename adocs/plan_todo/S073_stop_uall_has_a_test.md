id:         S073
goal:       the -uall porcelain read has a test that fails without it
accepts:    removing -uall from mode_stop's porcelain read fails a test; today all 308 pass, so the behaviour S060 added is unprotected; the test asserts what -uall changes rather than the flag itself
touches:    tests/test_s005_hooks.py
excludes:   changing the behaviour, which is correct as it stands
decisions:  
closes:     2026-08-08_adversarial.2-F07
blocks:
paused_by:
done:
