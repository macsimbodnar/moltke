id:         S025
goal:       documented exit-code semantics match the code
accepts:    README and MANUAL state the real rule, that diagnostics go to stderr and findings to stdout with exit 1 for both, traced to refuse() and run_validate; no documented claim about a stream contradicts the code path that produces it
touches:    README.md; MANUAL.md
excludes:   changing which stream any mode writes to, since something may already parse them
decisions:
closes:     2026-08-06_adversarial-F06
blocks:
paused_by:
done:      2026-08-06: README and MANUAL now state the real mapping — findings exit 1 on stdout, refusals exit 1 on stderr, blocks exit 2 on stderr — each traced to run_validate, refuse, and the hook modes, and derived from an eleven-invocation probe rather than from reading the code. New tests/test_s025_exit_codes.py pins it, red observed by routing refuse to stdout. Also documented: --post-write returns 2 but is non-blocking, and stderr can carry a warning on exit 0. Suite 173 OK, --validate green. README test count 163 to 173 and the exit-code line replaced with a table; MANUAL's one-line claim replaced with the table plus a scripting warning. specs needed no edit: no behaviour changed and it made no stream claim.
