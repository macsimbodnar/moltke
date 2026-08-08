id:         S080
goal:       a Stop state file that cannot be written does not wedge the session
accepts:    nothing in mode_stop raises: with .git unwritable, --stop prints every problem it collected and exits 2, never 1 and never a traceback, and the message says the state write failed rather than calling it a read and naming --validate, which reports all checks pass on that tree; the missing cap is stated in the message and scoped in specs per DEC-039, which extends DEC-031's accepted gap from no-git to anywhere the state cannot be written; the cap still fires normally where the state is writable, re-measured as 2 2 2 0 0; a test names moltke_stop_state.json, which no test does today; red observed with the finding's chmod 500 .git sequence
touches:    bin/moltke.py mode_stop state write; tests/test_s005_hooks.py
excludes:   moving the state outside the repository, which DEC-031 settled against
decisions:  DEC-039
closes:     2026-08-08_adversarial.3-F01
blocks:
paused_by:
done:      2026-08-08: mode_stop prints before it persists, and nothing in it raises. The retry state write was the one unguarded write left after S067 guarded every read, so an unwritable .git escaped to the backstop, which returns before the problems are printed and before the cap is consulted: the third wedge found here and the second introduced fixing the first. DEC-039 states a rule for the function rather than moving the guard again, and scopes the missing cap the way DEC-031 already scoped the no-git case — every Stop blocks, with the message naming the state file it could not write. 3 tests, red observed with chmod 500 .git, and the state file is named by a test for the first time. Suite 354 OK, --validate green. README test count 351 to 354; MANUAL known-issue entry widened from no-git to unwritable state; specs INV-12 line and a dated note.
