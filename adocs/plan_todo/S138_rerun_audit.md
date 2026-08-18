id:         S138
goal:       re-run the adversarial audit against the merged tree
accepts:    a fresh dated report under adocs/audit/ produced by the clean-context reviewer against the merged code, not against the pre-merge tree either branch audited; the surviving 2026-08-18 findings move to closed only if the re-run no longer reports them, and anything new lands in a step or a decision
touches:    adocs/audit/, adocs/plan.md, adocs/decisions.md
excludes:   fixing what it finds in the same step
decisions:  DEC-052
closes:
blocks:
paused_by:
done:
