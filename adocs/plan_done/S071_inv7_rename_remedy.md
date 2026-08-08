id:         S071
goal:       INV-7's remedy for a rename is a command that works
accepts:    INV-7 splits a porcelain rename line through porcelain_paths, so a git mv inside plan_done/ names the file that changed and prints a remedy that is a runnable command rather than `git checkout -- old -> new`, which truncates the renamed file when pasted; dropping R from the status codes fails a test, which it does not today; red observed with the shell command and the truncation
touches:    bin/moltke.py inv_7_done_immutable; tests/test_s003_invariants.py
excludes:   widening what counts as a legal change under plan_done/
decisions:  
closes:     2026-08-08_adversarial.2-F05
blocks:
paused_by:
done:      2026-08-08: INV-7's working-tree half reads porcelain through porcelain_paths, like both Stop gates and worktree_state already did. It sliced the line instead, so a rename inside plan_done/ named both halves and printed a remedy a shell reads as a redirection: git checkout -- old > new truncates the renamed file, which is the only remaining content of that step. The one invariant whose subject is immutable history printed a command that destroys a file in it, and repeated it to --stop as INV-12's actionable instruction. The violation now names the file that exists and says what it was renamed from. 4 tests, red observed on both the arrow and the redirection, and the R status code has cover for the first time. Suite 337 OK, --validate green. README test count 333 to 337; MANUAL needed no change; specs gained a dated note.
