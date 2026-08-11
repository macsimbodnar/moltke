id:         S120
goal:       the worklog subsystem is removed (DEC-046)
accepts:    acceptance criteria, testable
touches:    areas of the codebase
excludes:   explicitly out of scope
decisions:
closes:
blocks:
paused_by:
done:      2026-08-11: the worklog subsystem is removed (DEC-046). Gone: the UserPromptSubmit hook and --log-prompt, the recap gate and its dirty-tree false blocks, INV-15 and scan_secrets (retired, number never reused), the prompt-failure breadcrumbs, and --audit check's worklog classification. The Stop cap re-keys to a per-problem-set count in .git/ state — identical problems accumulate across turns, progress resets the count, and the linked-worktree property still holds. adocs/worklog.md and its template are deleted; forensic history is git. 32 tests deleted deliberately and named in testing.md, the cap and stamp tests retargeted, one new reconciliation test; golden refreshed after specs and MANUAL. Suite 414 OK, --validate green. README test count updated; MANUAL swept of every worklog, recap, and INV-15 passage; AGENTS.md §2/§9 wait for S123's single reissue.
