id:         S071
goal:       INV-7's remedy for a rename is a command that works
accepts:    INV-7 splits a porcelain rename line through porcelain_paths, so a git mv inside plan_done/ names the file that changed and prints a remedy that is a runnable command rather than `git checkout -- old -> new`, which truncates the renamed file when pasted; dropping R from the status codes fails a test, which it does not today; red observed with the shell command and the truncation
touches:    bin/moltke.py inv_7_done_immutable; tests/test_s003_invariants.py
excludes:   widening what counts as a legal change under plan_done/
decisions:  
closes:     2026-08-08_adversarial.2-F05
blocks:
paused_by:
done:
