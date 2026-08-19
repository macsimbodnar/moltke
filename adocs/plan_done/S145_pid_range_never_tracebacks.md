id:         S145
goal:       an out-of-range or non-positive --pid is refused at parse time, never a traceback
accepts:    an out-of-range or non-positive --pid is refused at parse time with the condition named, and _pid_alive treats an unusable pid as dead rather than raising; --stop, --session-start and --watch all survive a record carrying such a pid; MANUAL's claim that no mode ends in a Python traceback holds again; red observed first
touches:    bin/moltke.py _pid_alive, mode_watch argument validation
excludes:   validating pids that are plausible but already dead, which is the watcher's exit 3 path
decisions:
closes:     2026-08-19_adversarial-F05
blocks:
paused_by:
done:      2026-08-19 _pid_alive is total: a pid it cannot ask about reads dead, so a damaged
            watch record is reported instead of ending --stop and --session-start in an
            OverflowError past main's OSError backstop. --pid is validated with every other
            argument, before anything is armed: 0 and negatives are kill(2) process groups
            that answer alive forever so exit 3 could never fire, and a value past pid_t
            raised only after the record was on disk. watch_report's hand-rolled type and
            sign guard is gone, subsumed by the total probe. Closes 2026-08-19_adversarial-F05.
            Red observed first on both audit reproductions; specs and MANUAL state the
            refusal, README needed no change.
author:    Maksym Bodnar
