id:         S114
goal:       a pause that already resolved is reported and clearable
accepts:    A paused_by naming a step in plan_done/ makes --validate exit 1,
            saying the pause resolved, and --step unpause clears it; afterwards
            --validate exits 0 and the parent can be resumed or re-blocked.
            DEC-040 holds: a pause on live work is still refused. S070's
            step-over inside --step done is unchanged. Tests build the stale
            state and assert the report, the clear, and the unchanged paths; the
            report and clear fail without the fix.
touches:    bin/moltke.py unresolvable_pauses, inv_1 message, step_unpause;
            tests/test_s003_invariants.py
excludes:   changing how the state arises; --step block semantics
decisions:  DEC-040
closes:     2026-08-11_adversarial-F03
blocks:
paused_by:
done:
