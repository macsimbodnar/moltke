id:         S143
goal:       `--watch` registers through git_dir(), so a linked worktree is not "no .git found"
accepts:    `--watch` registers a record in a linked worktree and from a subdirectory of a marked repository, resolving through git_dir() rather than testing .git as a directory; the not-registered warning survives only for a genuinely ungitted tree; --stop reports a watcher armed from a worktree as lost or unacknowledged; red observed first
touches:    bin/moltke.py :1765 and :1903, _watch_record_path
excludes:   changing the watch record schema or where records live
decisions:
closes:     2026-08-19_adversarial-F03
blocks:
paused_by:
done:
