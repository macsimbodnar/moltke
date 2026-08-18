id:         S140
goal:       a watcher killed in its arm window still records an outcome
accepts:    a SIGTERM arriving between registration and handler installation ends the watcher through its own handler, so the record gains outcome `stopped`, `exit_code` 143, and `ended_at` — reproduced red first, deterministically rather than by waiting for the race (the existing kill test fails only under load, with `-15 != 143`); a kill before the record exists leaves no record at all, which is the correct answer since there is no obligation to acknowledge; the run of the suite that observes red records what it printed
touches:    bin/moltke.py mode_watch arm sequence, tests/test_s129_watch.py, adocs/testing.md
excludes:   SIGKILL, which no handler can catch and which the crashed-watcher report already covers; the ceiling bound on a single scan (S132)
decisions:  DEC-049
closes:
blocks:
paused_by:
done:
