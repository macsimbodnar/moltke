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
done:
