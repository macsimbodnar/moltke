id:         S025
goal:       documented exit-code semantics match the code
accepts:    README and MANUAL state the real rule, that diagnostics go to stderr and findings to stdout with exit 1 for both, traced to refuse() and run_validate; no documented claim about a stream contradicts the code path that produces it
touches:    README.md; MANUAL.md
excludes:   changing which stream any mode writes to, since something may already parse them
decisions:
closes:     2026-08-06_adversarial-F06
blocks:
paused_by:
done:
