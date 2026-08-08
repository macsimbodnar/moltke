id:         S083
goal:       --step new and --step block leave nothing behind when they refuse
accepts:    --step new and --step block write nothing until every write is known to be possible, as --step done has since S062 and S070: a refusal after the step file is written leaves an id no plan entry names, which is INV-3, and for block also an unpaused parent, which is INV-1; a repository green before a refused operation is green after it; red observed for both operations
touches:    bin/moltke.py step_new, step_block, append_to_plan; tests/test_s007_step.py
excludes:   reordering --step done, which is already correct
decisions:  
closes:     2026-08-08_adversarial.3-F04
blocks:
paused_by:
done:      2026-08-08: --step new and --step block write the plan entry first and the step file second, so a failure leaves nothing behind. Written the other way round, a failing append to plan.md left a step file no list entry names, which is INV-3, and for block an unpaused parent as well — the half-apply class S062 and S070 fixed for done and left in its two siblings. The order is chosen rather than arbitrary: a listed id with no file is recoverable, since INV-3 names it and --step new writes the file, while a file no plan lists has no command to clear it. 3 tests, red observed for both operations. Suite 365 OK, --validate green. README test count 362 to 365; MANUAL needed no change; specs gained a dated note.
