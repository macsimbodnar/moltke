id:         S035
goal:       moltke works in a linked worktree and a submodule
accepts:    the three .git-is-a-directory helpers resolve the git directory with git rev-parse --absolute-git-dir instead of guessing, so a linked worktree and a submodule get an audit baseline, a log-failure breadcrumb, and the Stop deadlock cap; --stop exit codes over five consecutive attempts with the same prompt_id read [2,2,2,0,0] in a linked worktree as they already do in a plain clone, which is INV-12 and DEC-006's no-deadlock property; the --audit new warning text stops claiming there is no git worktree where git works; a directory with no git at all still abstains; red observed in a real git worktree add, where the sequence is [2,2,2,2,2]
touches:    bin/moltke.py _log_failure_path, _stop_state_path, _audit_baseline_path and the audit_new warning; tests/test_s005_hooks.py; tests/test_s008_audit.py; MANUAL.md
excludes:   supporting a bare repository; caching the resolved git directory across modes
decisions:
closes:     2026-08-07_adversarial-F04
blocks:
paused_by:
done:
