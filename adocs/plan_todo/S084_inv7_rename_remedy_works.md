id:         S084
goal:       INV-7's rename remedy is a command that restores the file
accepts:    INV-7's remedy for a rename inside plan_done/ restores the file: `git checkout -- <new path>` changes nothing, and following both printed messages adds a second copy under the old name, which is an INV-6 duplicate id; the message names a command that undoes the rename; red observed by following the printed remedy and landing on INV-6
touches:    bin/moltke.py inv_7_done_immutable messages; tests/test_s003_invariants.py
excludes:   reverting S071, which fixed the truncating remedy
decisions:  
closes:     2026-08-08_adversarial.3-F05
blocks:
paused_by:
done:
