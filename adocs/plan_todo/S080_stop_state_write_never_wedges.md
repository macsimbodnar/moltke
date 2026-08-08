id:         S080
goal:       a Stop state file that cannot be written does not wedge the session
accepts:    the one unguarded write in mode_stop, the retry state file, cannot wedge a session: with .git unwritable, eight consecutive stops read 2 2 2 0 0 0 0 0 rather than 2 2 2 2 2 2 2 2, and the problems collected are printed either way; the message says the write failed rather than calling it a read and naming --validate, which reports all checks pass on that tree; a test names the state file, which no test does today; red observed with the finding's chmod 500 .git sequence
touches:    bin/moltke.py mode_stop state write; tests/test_s005_hooks.py
excludes:   moving the state outside the repository, which DEC-031 settled against
decisions:  
closes:     2026-08-08_adversarial.3-F01
blocks:
paused_by:
done:
