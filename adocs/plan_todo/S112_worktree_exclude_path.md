id:         S112
goal:       the local-file exclusion lands where git actually reads it
accepts:    In a linked worktree, --session-start writes the .moltke.local.md
            exclusion to the path `git rev-parse --git-path info/exclude`
            resolves, git status never shows the file, and the Stop gate does not
            block a clean turn. A test builds a linked worktree and asserts the
            porcelain is empty after --session-start; it fails without the fix.
            The primary-worktree behaviour is unchanged, held by the existing
            TestMachineLocalFile suite.
touches:    bin/moltke.py local_file_lines or git_dir sibling; tests/test_s005_hooks.py
excludes:   submodule fixtures, which the report reasons clean; changing what is
            injected
decisions:  DEC-043
closes:     2026-08-11_adversarial-F01
blocks:
paused_by:
done:
