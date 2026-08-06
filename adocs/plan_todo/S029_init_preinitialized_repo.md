id:         S029
goal:       init handles a repo already initialized on another machine
accepts:    the init skill's enabled-marker branch becomes a verification path for a fresh clone: state that repo state travels in git and only the plugin install is per-machine; run --validate and report; print the derived next step and the plan_current/ stack; compare the repo's AGENTS.md, CLAUDE.md, and .cursor/rules/moltke.mdc against the installed plugin's templates and report drift file by file without acting on it; a refresh is offered as a question, applied only on an explicit yes, and never touches adocs/ or .moltke.json; a disabled marker still means say so and stop; scaffold still never overwrites; drift detection covered by a test against a fixture scaffolded from older template content
touches:    skills/init/SKILL.md; bin/moltke.py (drift report, in --scaffold's kept-file path or a new op); tests/test_s006_init.py; MANUAL.md install section
excludes:   automatic template refresh without a yes; migrating adocs/ content between plugin versions; syncing any state between machines beyond what git already carries; verifying the plugin install itself, which S012 covered
decisions:
closes:
blocks:
paused_by:
done:
