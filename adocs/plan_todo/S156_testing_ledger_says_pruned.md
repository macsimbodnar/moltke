id:         S156
goal:       testing.md's header says what the tool does to it: rows leave with their plan entry, so "Append only" reads as write discipline, not as nothing is ever removed
accepts:    adocs/testing.md's header states that rows are pruned with their plan.md entry (DEC-048's last-5 window) while append-only stays the rule for writing them; templates/ carries the same wording wherever it ships that header
touches:    adocs/testing.md header, templates/adocs/testing.md if it ships one
excludes:   changing what prune_plan prunes, or the last-5 window itself
decisions:
closes:
blocks:
paused_by:
done:
