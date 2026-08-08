id:         S070
goal:       --step done leaves no state the CLI cannot clear
accepts:    --step done leaves no state that the CLI cannot clear: with the parent unpause still able to fail after the child has moved, the finding's read-only-parent fixture ends in a tree where neither --step done S001 nor --step done S002 helps; either the unpause moves ahead of the point of no return or the refusal names a command that fixes it; red observed with the finding's fixture, compared against the pre-S062 order which failed recoverably
touches:    bin/moltke.py step_done; tests/test_s007_step.py
excludes:   reverting S062, whose half-written completion was the defect
decisions:  
closes:     2026-08-08_adversarial.2-F04
blocks:
paused_by:
done:      2026-08-08: --step done pre-flights every file it will write, the step file and any paused parent, and refuses before touching anything if one is not writable. S062 put the write and the unlink ahead of the point of no return and left the unpause after it, so a failure there left the child in plan_done/ and the parent paused by a completed step — a state neither --step done nor --step start could clear, fixable only by hand-editing a step file, which is what --step exists to avoid. A pause naming a step already in plan_done/ is now treated as stale and reported rather than refused, so that state is recoverable however it is reached, including through the Bash writes no fence sees. 4 tests, red observed on all three symptoms. Suite 333 OK, --validate green. README test count 329 to 333; MANUAL needed no change, since it documents the refusal and not the write order; specs gained a dated note.
