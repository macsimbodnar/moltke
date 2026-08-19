id:         S144
goal:       `--audit check` reports the source a staged rename into tests/ removed
accepts:    `--audit check` reports the source path a staged rename removed, classifying a departure the way an unexpected deletion is classified today; an ordinary new file under tests/ stays expected; red observed first with a staged `git mv` of tracked source into tests/
touches:    bin/moltke.py worktree_state and its porcelain_paths use
excludes:   changing what counts as an expected reviewer write
decisions:
closes:     2026-08-19_adversarial-F04
blocks:
paused_by:
done:      worktree_state records both halves of a rename line: the destination with git's own status, the source as "removed by a rename to <destination>", and a departure is never newly here. Closes 2026-08-19_adversarial-F04 — one `git mv` of tracked source into tests/ reconciled as an expected new test and reported the removal nowhere. Red first: the audit's own reproduction exited 0. Five tests in TestAuditCheckSeesARenameSource, three of them controls. specs' --audit check row and MANUAL's consequences paragraph now say a rename is judged on both halves; README needed no change. 467 tests green.
author:    Maksym Bodnar
