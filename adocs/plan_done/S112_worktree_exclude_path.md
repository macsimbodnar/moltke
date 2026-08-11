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
done:      2026-08-11: the .moltke.local.md exclusion is written to git rev-parse --git-path info/exclude instead of --absolute-git-dir joined by hand, closing 2026-08-11_adversarial-F01. In a linked worktree the git dir is .git/worktrees/<name>/ whose info/exclude git status never reads, so the exclusion landed where nothing looked, the file showed ?? forever, the Stop gate blocked every clean turn, and its remedy steered toward committing the one file DEC-043 forbids in git. --git-path resolves per worktree the way git itself does; relative output is joined to the root, absolute kept. 1 test on a real linked-worktree fixture, red observed; the seven existing local-file tests hold the primary layout. Suite 446 OK, --validate green. README test count 445 to 446; MANUAL checked, no change — it documents the exclusion, not the path git implements it at.
