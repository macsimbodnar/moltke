id:         S093
goal:       INV-8's high-water-mark remedy prints the git blob spec, not the root-relative path
accepts:    In the nested-root fixture (git top level above the marked root), an
            INV-8 high-water-mark violation prints a git show command that exits 0
            and produces the file, as INV-7's twin messages already do.
            The message is unchanged when the marked root is the git top level.
            A test in the nested-root fixture asserts the printed spec resolves; it
            fails without the fix.
touches:    bin/moltke.py:512 (spec vs rel); tests/test_s003_invariants.py
excludes:   the deletion message at bin/moltke.py:482, which is already correct;
            any other INV-8 behaviour.
decisions:
closes:     2026-08-08_adversarial.4-F06
blocks:
paused_by:
done:      2026-08-09: INV-8's high-water-mark violation prints the git blob spec instead of the root-relative path, closing 2026-08-08_adversarial.4-F06. S081 threaded the top-level prefix through every other reader of decisions.md and missed this one message, so below the git top level the remedy for the hardest INV-8 violation answered fatal: path 'packages/foo/adocs/decisions.md' exists, but not 'adocs/decisions.md' — a remedy INV-12 calls actionable that could not run. The deletion message beside it was already correct, which is what made the gap easy to miss. 2 tests, red observed at 128 != 0 with that fatal quoted; the second is the non-vacuity anchor holding the ordinary case where the marked root is the top level, and both assert the high-water-mark branch fired rather than the deletion branch. Suite 399 OK, --validate green. README test count 397 to 399; MANUAL checked, no change — it does not quote this message; specs gained a dated note.
