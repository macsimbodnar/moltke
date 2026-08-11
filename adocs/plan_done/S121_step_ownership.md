id:         S121
goal:       steps are claimed at start and limits count per author (DEC-045)
accepts:    acceptance criteria, testable
touches:    areas of the codebase
excludes:   explicitly out of scope
decisions:
closes:
blocks:
paused_by:
done:      2026-08-11: steps are claimed at start (DEC-045). --step start stamps author: from git config user.name, gated on an actual repository because git config answers from the global config even outside one — the pre-existing solo refusal test caught exactly that. INV-1 counts non-paused steps per author with the unowned bucket keeping the solo shape; --step start refuses only against your own active steps; the SessionStart stack tags each step yours or with its owner. 5 tests, red observed on four. Suite 419 OK, --validate green. README's stale five-hooks and worklog lines corrected; MANUAL's --step start row and plan_active_max sentence state the claim model.
