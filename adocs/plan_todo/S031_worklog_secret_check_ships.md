id:         S031
goal:       the worklog secret check runs as an invariant, so it travels to every marked repository
accepts:    the shapes move from tests/test_s022_secrets.py into bin/moltke.py and run as a numbered invariant, so --validate reports them and --stop refuses on them in any marked repository; the suite test keeps working by importing the shapes, so the detector has exactly one definition and its non-vacuity guard still covers the shipped version; a hit names the shape, the line, and a truncated match, never the whole value; the check reads adocs/worklog.md only, and a clean worklog stays silent; specs gains the invariant and MANUAL's known-issues entry stops saying the check does not travel; red observed by planting a synthetic key and watching --validate and --stop report it
touches:    bin/moltke.py; tests/test_s022_secrets.py; adocs/specs.md; MANUAL.md
excludes:   redaction at write time, which DEC-024 rejected; entropy or bare-hex heuristics, which false-positive on the commit shas every recap carries; scanning anything beyond the worklog
decisions:  DEC-024, DEC-032
closes:
blocks:
paused_by:
done:
