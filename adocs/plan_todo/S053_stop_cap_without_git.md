id:         S053
goal:       the Stop deadlock cap exists in a marked repository without git
accepts:    five consecutive stops in a marked repository with no git at all read 2 2 2 0 0, as they do in a clone, a linked worktree, and a submodule since S035; INV-12 and DEC-006 make no-deadlock unconditional, and a repository without git is the one case S035 left; wherever the state goes it is not a tracked file, so it never appears in git status or in an audit footprint; red observed as 2 2 2 2 2 2
touches:    bin/moltke.py _stop_state_path; tests/test_s005_hooks.py TestStop; MANUAL.md
excludes:   storing state outside the repository, which would leak between projects
decisions:
closes:     2026-08-07_adversarial.2-F06
blocks:
paused_by:
done:
