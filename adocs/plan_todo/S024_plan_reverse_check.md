id:         S024
goal:       a plan.md id with no step file is a violation
accepts:    an id listed in plan.md with no file in any of the three plan directories is reported by INV-3, naming the id and the fix; the existing forward direction still holds; a phantom id no longer becomes the derived next step silently
touches:    bin/moltke.py inv_3_steps_in_plan; tests/test_s003_invariants.py
excludes:   changing derived_next itself; validating plan.md ordering or numbering
decisions:
closes:     2026-08-06_adversarial-F11
blocks:
paused_by:
done:
