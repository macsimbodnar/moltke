id:         S156
goal:       testing.md's header says what the tool does to it: rows leave with their plan entry, so "Append only" reads as write discipline, not as nothing is ever removed
accepts:    adocs/testing.md's header states that rows are pruned with their plan.md entry (DEC-048's last-5 window) while append-only stays the rule for writing them; templates/ carries the same wording wherever it ships that header
touches:    adocs/testing.md header, templates/adocs/testing.md if it ships one
excludes:   changing what prune_plan prunes, or the last-5 window itself
decisions:
closes:
blocks:
paused_by:
done:      2026-08-20. The ledger header said "Append only." and nothing else, which reads as nothing is ever removed — false since S126/DEC-048: prune_plan drops a row when one completion prunes the plan.md entry of every step that row names (newest-5-done window, PLAN_DONE_KEPT = 5). Header now separates the two: append only is how rows are written, not a promise a row stays, and plan_done/ plus git hold the history. templates/adocs/testing.md carries the same paragraph without the DEC id (DEC-002) and loses its "A step cannot complete without a row referencing its id" sentence, which INV-5 stopped enforcing at S125 (inv_5_done_evidence is stamp-present only). MANUAL's Teams section justified the testing.md union merge as "append-only rows" the same wrong way; corrected in place, and it now says a union merge can restore a row the other side pruned. README already read voluntary and needed nothing. Suite 527 OK, --validate green.
author:    Maksym Bodnar
