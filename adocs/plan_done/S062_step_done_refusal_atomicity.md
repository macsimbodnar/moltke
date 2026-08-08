id:         S062
goal:       --step done refuses before it writes, so a failed completion leaves INV-1 satisfied
accepts:    every check --step done can fail runs before the done: stamp is written and before a paused parent is unpaused, so the S052 OSError refusal path no longer leaves plan_current/ holding two non-paused steps; a repository that was green before a refused completion is green after it, asserted with --validate exit 0 on the same tree; the existing refusal messages and their exit codes are unchanged; red observed with the missing plan_done/ fixture, where the repository goes from all checks pass to an INV-1 violation
touches:    bin/moltke.py step_done ordering; tests/test_s007_step.py
excludes:   rolling back a partially written tree after the fact, rather than not writing until the move is certain
decisions:
closes:     2026-08-08_adversarial-F03
blocks:
paused_by:
done:      2026-08-08: --step done writes nothing until the move is certain. It stamped, unpaused, and renamed last, and the rename is the only one that can fail, so S052's refusal arrived after two mutations were on disk — a transition that refused and repaired half of itself, taking the repository from all checks pass to an INV-1 violation. The stamped content now goes straight to plan_done/, so the first action is the failing one; the source is unlinked only once the destination exists, with the copy undone if that fails; the parent is unpaused after both. set_field split into a pure with_field and a write to make that ordering possible. 4 tests, red observed on all three symptoms. Suite 297 OK, --validate green. README test count 293 to 297; MANUAL needed no change, since it documents the refusal and not the write order; specs gained a dated note.
