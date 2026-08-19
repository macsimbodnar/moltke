id:         S143
goal:       `--watch` registers through git_dir(), so a linked worktree is not "no .git found"
accepts:    `--watch` registers a record in a linked worktree and from a subdirectory of a marked repository, resolving through git_dir() rather than testing .git as a directory; the not-registered warning survives only for a genuinely ungitted tree; --stop reports a watcher armed from a worktree as lost or unacknowledged; red observed first
touches:    bin/moltke.py :1765 and :1903, _watch_record_path
excludes:   changing the watch record schema or where records live
decisions:
closes:     2026-08-19_adversarial-F03
blocks:
paused_by:
done:      2026-08-19: closes 2026-08-19_adversarial-F03. _watch_record_path and watch_records both resolve through git_dir(root) instead of testing .git for directory-ness, so a linked worktree, a submodule and a marked root below the git top level all register under moltke_watch/ in the git directory git reports rather than reporting 'no .git found' with the git directory present. watch_report gained a fallback: a worktree's git directory sits outside its checkout, so relative_to(root) raised ValueError once records could exist there, and the line prints the absolute path instead — every line there names something to delete, so hiding the obligation was not an option. Red observed first on both of the reviewer's TestWatchStateInALinkedWorktree tests, the second establishing that the same worktree ends a turn clean before anything is armed, so the exit 0 it then saw was the missing report and not a clean tree. The code landed in 79e9d46 with S141 rather than here, because one reviewer test file gates both findings and the completion gate reads the whole suite (DEC-058); this step carries the plan move and the doc trace. specs.md's --watch row, MANUAL's watcher paragraph and AGENTS.md §12 all said .git/moltke_watch/ and now name the git directory git reports, with templates/AGENTS.md kept byte-identical. Suite 457 OK (3 skip), --validate green. README checked, no change: it documents no watch paths.
author:    Maksym Bodnar
