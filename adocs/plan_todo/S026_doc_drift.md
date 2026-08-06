id:         S026
goal:       documentation drift pass
accepts:    MANUAL's install section states the hosted git URL rather than a conditional; plugin.json carries a repository field, after verifying it is a valid manifest key against the live plugin reference; adocs/plan_todo/ exists here as the file map and README claim; no live doc statement remains that the code contradicts
touches:    MANUAL.md; .claude-plugin/plugin.json; adocs/plan_todo/.gitkeep; README.md
excludes:   the version bump, which is S027; any restructuring of the plugin root, which DEC-020 settled
decisions:
closes:     2026-08-06_adversarial-F13
blocks:
paused_by:
done:
