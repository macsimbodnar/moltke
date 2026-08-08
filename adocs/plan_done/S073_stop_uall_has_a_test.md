id:         S073
goal:       the -uall porcelain read has a test that fails without it
accepts:    removing -uall from mode_stop's porcelain read fails a test; today all 308 pass, so the behaviour S060 added is unprotected; the test asserts what -uall changes rather than the flag itself
touches:    tests/test_s005_hooks.py
excludes:   changing the behaviour, which is correct as it stands
decisions:  
closes:     2026-08-08_adversarial.2-F07
blocks:
paused_by:
done:      2026-08-08: the -uall porcelain read has a test. Plain porcelain collapses a wholly untracked directory into one entry, so the stamp gate saw  and nothing inside it; S060 passed -uall for that reason and nothing held the flag in place, so reverting it left all 308 tests green. This gate and worktree_state are the only -uall readers, which is exactly how a later tidy-up would have restored the blind spot silently. Test-only step, no behaviour change. Red observed in a copy with -uall removed: . Suite 339 OK, --validate green. README test count 338 to 339; MANUAL and specs needed no change, since S060's note already describes the behaviour this now guards.
