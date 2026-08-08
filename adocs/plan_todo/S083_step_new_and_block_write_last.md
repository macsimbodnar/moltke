id:         S083
goal:       --step new and --step block leave nothing behind when they refuse
accepts:    --step new and --step block write nothing until every write is known to be possible, as --step done has since S062 and S070: a refusal after the step file is written leaves an id no plan entry names, which is INV-3, and for block also an unpaused parent, which is INV-1; a repository green before a refused operation is green after it; red observed for both operations
touches:    bin/moltke.py step_new, step_block, append_to_plan; tests/test_s007_step.py
excludes:   reordering --step done, which is already correct
decisions:  
closes:     2026-08-08_adversarial.3-F04
blocks:
paused_by:
done:
