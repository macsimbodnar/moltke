id:         S026
goal:       documentation drift pass
accepts:    MANUAL's install section states the hosted git URL rather than a conditional; plugin.json carries a repository field, after verifying it is a valid manifest key against the live plugin reference; adocs/plan_todo/ exists here as the file map and README claim; no live doc statement remains that the code contradicts
touches:    MANUAL.md; .claude-plugin/plugin.json; adocs/plan_todo/.gitkeep; README.md
excludes:   the version bump, which is S027; any restructuring of the plugin root, which DEC-020 settled
decisions:
closes:     2026-08-06_adversarial-F13
blocks:
paused_by:
done:      2026-08-07: plugin.json gains repository, verified against the live manifest field table and re-validated with claude plugin validate; MANUAL's install section states the hosted URL, checked reachable unauthenticated, and keeps the local-checkout form for developing moltke itself; .gitkeep added to the three plan directories so this repo matches what SCAFFOLD_DIRS creates. The sweep found two items the finding missed: README claimed Python 3.12 while the suite runs on 3.9.6, now stated as 3.9 and 3.14 both green with no lower bound tested, and twelve Python 3.12 .pyc files were tracked since S013 and shipped into every install under DEC-020, now removed and gitignored. README and MANUAL both edited in this commit; README's no-environment-variables, five-hook-events, and three-skills claims re-verified against code.
