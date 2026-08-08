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
done:
