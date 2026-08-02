id:         S013
goal:       rename the workflow directory project/ to adocs/ everywhere, with no migration path
accepts:    `--scaffold` creates `adocs/` and never `project/`; every path and user-facing message in `bin/moltke.py` reads `adocs/`; the full suite is green with every fixture on the new path; a guard test fails if any live file outside history still names `project/`; `AGENTS.md` and `templates/AGENTS.md` stay byte-identical; this repository's own state is moved with `git mv` and `--validate` exits 0 at the commit; `worklog.md` and `decisions.md` are byte-identical across the move (INV-8 has no baseline for one commit and abstains); `plugin.json` version is 0.2.0
touches:    bin/moltke.py, tests/, AGENTS.md, templates/, skills/, agents/, README.md, MANUAL.md, .claude-plugin/plugin.json, this repository's adocs/
excludes:   any migration mode for repositories already scaffolded with `project/` (none exist, DEC-021); rewriting `project/` inside plan_done/, or inside worklog.md and decisions.md entries predating DEC-021, which are history; re-verifying the install, which is S012
decisions:  DEC-021
closes:
blocks:     S012
paused_by:
done:      2026-08-02: project/ renamed to adocs/ (DEC-021). bin/moltke.py routes every path through one DOCS constant; templates/adocs/, tests, AGENTS.md and templates/AGENTS.md byte-identical. 112 tests green, --validate exit 0. README checked: test count corrected 110 to 112. MANUAL checked: two known issues added (no 0.1.0 migration, hooks run the installed copy), live-hook entry narrowed to what was observed.
