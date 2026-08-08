id:         S082
goal:       --step block refuses on an already-paused parent instead of breaking INV-1
accepts:    --step block on a parent that is already paused refuses, instead of reporting success while overwriting the parent's paused_by and leaving plan_current/ with two non-paused steps; the repository is green before and after the refusal; red observed with the finding's fixture, where a green tree becomes INV-1 with exit 0 and a success message
touches:    bin/moltke.py step_block; tests/test_s007_step.py TestBlock
excludes:   changing what plan_stack_max permits
decisions:  
closes:     2026-08-08_adversarial.3-F03
blocks:
paused_by:
done:      2026-08-08: --step block refuses when the parent is already paused. It asked only that the parent was in plan_current/ and then overwrote its paused_by, so a second blocking child reported success while taking the repository from all checks pass to an INV-1 violation: the first pause vanished, the parent unpaused itself, and both children counted as active. A step is blocked by one child at a time, and the refusal names the remedy, which is blocking that child instead. 3 tests, red observed on both the exit code and the erased field. Suite 362 OK, --validate green. README test count 359 to 362; MANUAL needed no change, since it says --step refuses rather than repairs and now that is true here too; specs gained a dated note.
