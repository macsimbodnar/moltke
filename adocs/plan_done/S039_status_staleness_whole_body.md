id:         S039
goal:       status.md staleness is judged on the whole file, not one line
accepts:    a status.md whose In progress or Last done disagrees with plan_current/ is reported stale by --session-start and refused by --stop, not only one whose Next: line disagrees; the comparison is against what --step status would regenerate, ignoring the Updated: line and the human-written Parked block; regenerating clears it; red observed with the state this repository was in during the S027 run, where status.md said 'In progress: none' while S027 sat in plan_current/ and nothing complained
touches:    bin/moltke.py status_next, mode_session_start, mode_stop, step_status; tests/test_s005_hooks.py; tests/test_s007_step.py
excludes:   rewriting status.md automatically from a hook, which would hide the disagreement rather than report it
decisions:
closes:     2026-08-07_adversarial-F08
blocks:
paused_by:
done:      2026-08-07: status.md staleness is judged on all four derived fields against exactly what --step status would write, sharing one status_lines; the Updated line and the Parked block are ignored. 6 tests, red observed. Suite 212 OK, --validate green, and the finding's own state now named by both --session-start and --stop. README test count 206 to 212; MANUAL's daily-use line now says which fields are compared and which are the human's. Two regressions the stricter check exposed were fixed rather than worked around: the fresh-scaffold wording and Last done reading prose ids.
