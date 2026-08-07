id:         S042
goal:       the test_command refusal obeys the documented stream mapping
accepts:    the suite-gate banner and the refusal land on the same stream, so a refusal writes nothing to stdout as README and MANUAL state; TestRefusalsGoToStderr gains the test_command case, which is the one path that would have failed its existing assertion and was absent from it; red observed by adding that case before changing the code
touches:    bin/moltke.py run_test_command; tests/test_s025_exit_codes.py TestRefusalsGoToStderr
excludes:   changing any other mode's streams, which S025 ruled out because something may already parse them
decisions:
closes:     2026-08-07_adversarial-F11
blocks:
paused_by:
done:
