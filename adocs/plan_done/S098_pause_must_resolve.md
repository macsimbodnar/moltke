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
done:      2026-08-09: INV-1's pause rule is now 'the pause resolves' rather than 'the pauser exists', and --step unpause clears exactly what INV-1 reports, closing 2026-08-09_adversarial-F02. S090 closed the phantom pauser and left the neighbour: a step whose paused_by names itself, or a ring of steps pausing each other, satisfies that rule because every pauser exists, and is just as stuck — none counts as active so INV-1 and INV-2 say nothing, while --step done sends you to the pauser and --step unpause sends you back to --step done, the two commands naming each other. Reachable by a one-token slip, since AGENTS.md tells the agent to set paused_by on the parent and the file being edited is the parent. unresolvable_pauses is shared by the invariant and by the command, so the remedy the violation prints is the remedy that runs rather than a second description of it. DEC-040 is kept: a pause resolving to live work is still refused, which is the non-vacuity anchor. A pauser in plan_done/ terminates the walk, so S070's stale pause is unchanged. 7 tests, red observed on four. Suite 422 OK, --validate green. README test count 415 to 422; MANUAL's --step unpause row states the widened case; specs gained a dated note.
