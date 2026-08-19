id:         S144
goal:       `--audit check` reports the source a staged rename into tests/ removed
accepts:    `--audit check` reports the source path a staged rename removed, classifying a departure the way an unexpected deletion is classified today; an ordinary new file under tests/ stays expected; red observed first with a staged `git mv` of tracked source into tests/
touches:    bin/moltke.py worktree_state and its porcelain_paths use
excludes:   changing what counts as an expected reviewer write
decisions:
closes:     2026-08-19_adversarial-F04
blocks:
paused_by:
done:
