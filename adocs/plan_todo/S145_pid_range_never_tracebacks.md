id:         S145
goal:       an out-of-range or non-positive --pid is refused at parse time, never a traceback
accepts:    an out-of-range or non-positive --pid is refused at parse time with the condition named, and _pid_alive treats an unusable pid as dead rather than raising; --stop, --session-start and --watch all survive a record carrying such a pid; MANUAL's claim that no mode ends in a Python traceback holds again; red observed first
touches:    bin/moltke.py _pid_alive, mode_watch argument validation
excludes:   validating pids that are plausible but already dead, which is the watcher's exit 3 path
decisions:
closes:     2026-08-19_adversarial-F05
blocks:
paused_by:
done:
