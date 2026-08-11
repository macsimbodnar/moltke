id:         S127
goal:       plan_steps memoized per process, and --version exists
accepts:    acceptance criteria, testable
touches:    areas of the codebase
excludes:   explicitly out of scope
decisions:
closes:
blocks:
paused_by:
done:      2026-08-11: plan_steps is cached per root and per process — run_checks parsed every step file ~8 times per run, ~1,000 reads per --stop at this project's size — with the five plan mutators invalidating, pinned by a test that counts parses and by unpause's read-write-read path. --version exists and answers which moltke am I talking to before any gate, the question every stale-cache session of the last two days needed; golden refreshed after specs and MANUAL. --stop measured at 0.24s. --json stays deferred until a consumer exists. Suite 398 OK, --validate green.
author:    Maksym Bodnar
