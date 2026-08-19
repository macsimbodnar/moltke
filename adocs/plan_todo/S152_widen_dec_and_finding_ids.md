id:         S152
goal:       DEC and finding id scanners are not blind past their width, and AGENTS.md 5's lint claim is enforced or dropped
accepts:    the DEC and finding id scanners read ids at any width, or an unreadable id is a reported violation rather than a silently skipped line; the dead git_dir at :1013 and the doubled assignment are gone; AGENTS.md section 5 either names a linter the completion gate runs or drops the word lint, with templates/AGENTS.md following; red observed first
touches:    bin/moltke.py DEC and finding id patterns, AGENTS.md, templates/AGENTS.md
excludes:   renumbering any existing DEC or finding id
decisions:
closes:     2026-08-19_adversarial-F12
blocks:
paused_by:
done:
