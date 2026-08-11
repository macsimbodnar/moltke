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
done:      2026-08-11: a pause whose pauser is already in plan_done/ is reported by INV-1 as resolved and cleared by --step unpause, closing 2026-08-11_adversarial-F03. The state is one --step done's own failure path documents leaving behind, and in it the parent showed Blocked: forever while unpause and block both prescribed a --step done that refuses on a completed step — the S098 signature through the one door it left. unresolvable_pauses gains the stale kind, shared by the invariant and the command as before, so the printed remedy is the remedy that runs; a stale pauser no longer terminates the walk silently, it reports. S070's step-over inside --step done is unchanged and pinned, and DEC-040's live-work refusal is untouched. 3 tests, red observed on the report-and-clear path. Suite 451 OK, --validate green. README test count 449 to 451; MANUAL's --step unpause row already says exactly the cases --validate reports, which now includes this one, so no change.
