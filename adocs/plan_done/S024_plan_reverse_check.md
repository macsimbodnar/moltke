id:         S024
goal:       a plan.md id with no step file is a violation
accepts:    an id listed in plan.md with no file in any of the three plan directories is reported by INV-3, naming the id and the fix; the existing forward direction still holds; a phantom id no longer becomes the derived next step silently
touches:    bin/moltke.py inv_3_steps_in_plan; tests/test_s003_invariants.py
excludes:   changing derived_next itself; validating plan.md ordering or numbering
decisions:
closes:     2026-08-06_adversarial-F11
blocks:
paused_by:
done:      2026-08-06: INV-3 gained its reverse direction, so an id in plan.md with no step file is a violation naming both fixes; ids still read through strip_guidance so a commented example is not a phantom. 4 tests, red observed as 'moltke: all checks pass'. Probed in a throwaway repo that --validate, --post-write, and --stop all name the phantom while --session-start still announces it, which is recorded as a residual since derived_next is excluded. Suite 163 OK, --validate green. README test count 160 to 163; MANUAL checked, no change needed — it describes INV-3 nowhere by direction, only that the turn will not end on an invariant violation.
