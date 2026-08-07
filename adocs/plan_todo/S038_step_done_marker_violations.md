id:         S038
goal:       a malformed test_command refuses completion instead of disabling the gate
accepts:    --step done refuses when test_command is present but not a non-empty string, naming the malformed value and distinguishing it from the key being absent; the four malformed values in the finding all refuse, and the step stays in plan_current/; an absent key behaves exactly as today; mode_step receives marker violations the way --validate, --post-write, and --stop already do, so no marker violation is invisible to the one command that gates completion; red observed with each of '' , '   ', a list, and 0, all of which complete green today while reporting that the key is absent
touches:    bin/moltke.py mode_step, run_test_command, main dispatch; tests/test_s007_step.py TestDoneTestCommandGate
excludes:   making test_command required; validating the command string beyond its type
decisions:
closes:     2026-08-07_adversarial-F07
blocks:
paused_by:
done:
