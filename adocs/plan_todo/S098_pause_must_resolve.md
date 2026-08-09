id:         S098
goal:       a pause has to resolve: no step pauses itself, and no cycle of pauses
accepts:    A step in plan_current/ carrying paused_by naming itself makes
            --validate exit 1, naming the step and the command that clears it.
            Two steps in plan_current/ pausing each other make --validate exit 1,
            naming both members of the cycle rather than one of them.
            --step unpause clears a pause --validate reports, so the dead end is
            gone: after running it --validate exits 0 and --step done on the step
            succeeds. DEC-040's rule is kept — a pause naming reachable, live
            work is still refused — so this widens what unpause clears to exactly
            what INV-1 reports.
            The legitimate shape stays silent: a parent paused by a child that is
            itself unpaused leaves --validate at exit 0, and S090's phantom-pauser
            behaviour is unchanged.
            Tests build the self-pause and the two-step cycle and assert exit 1;
            they fail without the fix.
touches:    bin/moltke.py inv_1_active_max pauser rule, step_unpause;
            tests/test_s003_invariants.py
excludes:   changing how INV-1 counts a legitimately paused step; a general
            unpause that clears any pause, which DEC-040 rejected and this must
            not reintroduce; changing --step block, which already refuses an
            already-paused parent (S082)
decisions:  DEC-040
closes:     2026-08-09_adversarial-F02
blocks:
paused_by:
done:
