id:         S084
goal:       INV-7's rename remedy is a command that restores the file
accepts:    INV-7's remedy for a rename inside plan_done/ restores the file: `git checkout -- <new path>` changes nothing, and following both printed messages adds a second copy under the old name, which is an INV-6 duplicate id; the message names a command that undoes the rename; red observed by following the printed remedy and landing on INV-6
touches:    bin/moltke.py inv_7_done_immutable messages; tests/test_s003_invariants.py
excludes:   reverting S071, which fixed the truncating remedy
decisions:  
closes:     2026-08-08_adversarial.3-F05
blocks:
paused_by:
done:      2026-08-08: INV-7 names git mv for a rename inside plan_done/, which undoes it, rather than git checkout on the new path, which restores it from an index that already holds the rename and so changes nothing. S071 made the message safe to paste and left it a no-op, and following it together with the deletion message wrote the old name back beside the new one — an INV-6 duplicate id, further from green than before. A rename now reports once, as a rename, and a test runs the printed command and asserts the tree ends green rather than asserting the string looks right. 2 tests, red observed on both the no-op and the duplicate id. Suite 367 OK, --validate green. README test count 365 to 367; MANUAL needed no change; specs gained a dated note.
