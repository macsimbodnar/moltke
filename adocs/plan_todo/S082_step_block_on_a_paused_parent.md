id:         S082
goal:       --step block refuses on an already-paused parent instead of breaking INV-1
accepts:    --step block on a parent that is already paused refuses, instead of reporting success while overwriting the parent's paused_by and leaving plan_current/ with two non-paused steps; the repository is green before and after the refusal; red observed with the finding's fixture, where a green tree becomes INV-1 with exit 0 and a success message
touches:    bin/moltke.py step_block; tests/test_s007_step.py TestBlock
excludes:   changing what plan_stack_max permits
decisions:  
closes:     2026-08-08_adversarial.3-F03
blocks:
paused_by:
done:
