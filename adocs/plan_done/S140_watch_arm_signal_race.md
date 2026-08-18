id:         S140
goal:       a watcher killed in its arm window still records an outcome
accepts:    a SIGTERM arriving between registration and handler installation ends the watcher through its own handler, so the record gains outcome `stopped`, `exit_code` 143, and `ended_at` — reproduced red first, deterministically rather than by waiting for the race (the existing kill test fails only under load, with `-15 != 143`); a kill before the record exists leaves no record at all, which is the correct answer since there is no obligation to acknowledge; the run of the suite that observes red records what it printed
touches:    bin/moltke.py mode_watch arm sequence, tests/test_s129_watch.py, adocs/testing.md
excludes:   SIGKILL, which no handler can catch and which the crashed-watcher report already covers; the ceiling bound on a single scan (S132)
decisions:  DEC-049
closes:
blocks:
paused_by:
done:      A SIGTERM between the registration write and the handler install killed the watcher through the default disposition: the record kept its armed_at and gained no outcome, so watch_report read a clean stop as 'watcher died without recording an outcome'. Handlers now go up before registration, and the registration itself moved inside the try, so the finally that writes the outcome covers the arm window. The finally writes only into a record that reached the disk: a kill before the write leaves nothing armed, and inventing a record there would block a stop for a run that never started. Red was deterministic rather than load-dependent — a driver patches _watch_write to send SIGTERM to itself from inside the registration write, so the window is hit every run; both new tests printed -15 != 143, death by signal instead of the handler's 143. MANUAL's watcher lint reference said INV-13, retired with the fence police; corrected to INV-17, the number DEC-052 re-issued it under.
author:    Maksym Bodnar
