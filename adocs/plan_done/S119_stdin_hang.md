id:         S119
goal:       --pre-write consults PATH before reading stdin
accepts:    acceptance criteria, testable
touches:    areas of the codebase
excludes:   explicitly out of scope
decisions:
closes:
blocks:
paused_by:
done:      2026-08-11: --pre-write consults PATH before stdin, closing the product review's observed hang. With a PATH argument stdin is never read — nothing it could add, including agent_type, comes from manual callers. Hooks pass no PATH and are unchanged, held by the existing TestPreWrite stdin tests. 1 test, red observed as a 10s TimeoutExpired. Suite green via the done gate. README and MANUAL checked, no change.
