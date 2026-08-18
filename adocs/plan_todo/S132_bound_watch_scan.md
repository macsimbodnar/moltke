id:         S132
goal:       bound each --watch scan so the ceiling holds against a runaway regex or a huge log
accepts:    a watcher armed with a catastrophically backtracking caller regex against a non-matching log still exits 124 at its ceiling, observed red first (today it runs past the ceiling until an outer kill); the bound is out of band from the poll loop, so a scan that never returns cannot outlive the deadline; a scan bounded mid-flight is reported as the ceiling, never as a silent no-match; the record under `.git/moltke_watch/` gets the same outcome it would on any other ceiling exit; the per-poll cost of a large log is stated in MANUAL rather than left to be discovered
touches:    bin/moltke.py _watch_scan and mode_watch, tests/test_s129_watch.py, MANUAL.md
excludes:   rejecting caller regexes by shape (guessing which patterns backtrack is not the fix); incremental or offset-based scanning, which would give up catching a marker written before arming
decisions:  DEC-049
closes:     2026-08-18_adversarial-F02
blocks:
paused_by:
done:
