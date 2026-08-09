id:         S090
goal:       a paused_by naming no step file is reported and clearable
accepts:    A step in plan_current/ carrying paused_by: S999, with no S999 file in
            any plan directory, makes --validate exit 1 with a violation that names
            the step, the missing pauser, and the command that clears it.
            The named command actually clears it: after running it, --validate
            exits 0 and --step done on the parent succeeds.
            The existing S070 stale-pause path (pauser already in plan_done/) keeps
            its current behaviour.
            A test builds the state and asserts --validate exits 1; it fails
            without the fix.
touches:    bin/moltke.py invariant checks (INV-1 neighbourhood) and/or step_done's
            stale-pause path; tests/test_s003_invariants.py
excludes:   the CLI route into this state, which is S088; changing how INV-1 counts
            a legitimately paused step.
decisions:
closes:     2026-08-08_adversarial.4-F03
blocks:
paused_by:
done:      2026-08-09: INV-1 reports a paused_by naming a step that is in no plan directory, and --step unpause <id> clears it (DEC-040), closing 2026-08-08_adversarial.4-F03. A pause is what takes a step out of the active count, and nothing checked the pauser existed, so a step could sit parked behind work that was never created: all checks pass, --roadmap drawing it as paused by a phantom, --step done on the parent refusing and sending you to a step no operation could reach, and hand-editing the only way out — tracked state saying something untrue, which is the prime directive. unpause is narrow by design: it refuses a pause whose step exists, because a general unpause would be a way around INV-1 rather than a repair. S070's stale-pause path is untouched and pinned by a test. 5 tests, red observed on three; two are non-vacuity anchors, and one of those first asserted nothing because it patched a line the fixture never writes. Suite 392 OK, --validate green. README test count 387 to 392; MANUAL gained the --step unpause row; specs gained a dated note and a surface table entry; the CLI golden was refreshed after both.
