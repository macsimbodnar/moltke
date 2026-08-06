id:         S023
goal:       surface guard covers skills, hooks, and marker keys
accepts:    adding, renaming, or removing a skill, a hook event, or a recognised .moltke.json key fails the golden; each must also appear in specs.md and MANUAL.md, so refreshing the golden alone never makes the suite green; red observed by tampering with each of the three component kinds
touches:    tests/test_s009_surface.py current_surface and assert_documented; tests/golden/cli_surface.txt; tests/test_s010_plugin.py; adocs/specs.md; MANUAL.md
excludes:   guarding skill body content or hook command strings; anything the CLI golden already covers
decisions:
closes:     2026-08-06_adversarial-F10
blocks:
paused_by:
done:
