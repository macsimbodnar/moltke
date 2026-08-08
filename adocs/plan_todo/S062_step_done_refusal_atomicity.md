id:         S062
goal:       --step done refuses before it writes, so a failed completion leaves INV-1 satisfied
accepts:    every check --step done can fail runs before the done: stamp is written and before a paused parent is unpaused, so the S052 OSError refusal path no longer leaves plan_current/ holding two non-paused steps; a repository that was green before a refused completion is green after it, asserted with --validate exit 0 on the same tree; the existing refusal messages and their exit codes are unchanged; red observed with the missing plan_done/ fixture, where the repository goes from all checks pass to an INV-1 violation
touches:    bin/moltke.py step_done ordering; tests/test_s007_step.py
excludes:   rolling back a partially written tree after the fact, rather than not writing until the move is certain
decisions:
closes:     2026-08-08_adversarial-F03
blocks:
paused_by:
done:
