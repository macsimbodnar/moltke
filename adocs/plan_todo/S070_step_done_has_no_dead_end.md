id:         S070
goal:       --step done leaves no state the CLI cannot clear
accepts:    --step done leaves no state that the CLI cannot clear: with the parent unpause still able to fail after the child has moved, the finding's read-only-parent fixture ends in a tree where neither --step done S001 nor --step done S002 helps; either the unpause moves ahead of the point of no return or the refusal names a command that fixes it; red observed with the finding's fixture, compared against the pre-S062 order which failed recoverably
touches:    bin/moltke.py step_done; tests/test_s007_step.py
excludes:   reverting S062, whose half-written completion was the defect
decisions:  
closes:     2026-08-08_adversarial.2-F04
blocks:
paused_by:
done:
