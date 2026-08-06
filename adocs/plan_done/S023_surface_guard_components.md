id:         S023
goal:       surface guard covers skills, hooks, and marker keys
accepts:    adding, renaming, or removing a skill, a hook event, or a recognised .moltke.json key fails the golden; each must also appear in specs.md and MANUAL.md, so refreshing the golden alone never makes the suite green; red observed by tampering with each of the three component kinds
touches:    tests/test_s009_surface.py current_surface and assert_documented; tests/golden/cli_surface.txt; tests/test_s010_plugin.py; adocs/specs.md; MANUAL.md
excludes:   guarding skill body content or hook command strings; anything the CLI golden already covers
decisions:
closes:     2026-08-06_adversarial-F10
blocks:
paused_by:
done:      2026-08-06: golden covers declared skills, hook events, and MARKER_KEYS, with the specs-and-MANUAL cross-check applied to each; declarations centralised in tests/surface.py and read by both the golden and the plugin tests. MARKER_KEYS pinned load-bearing by a per-key validation test. Red observed for all three tamper kinds, plus the pre-fix baseline where deleting the Stop hook left the suite green. Suite 160 OK, --validate green. README test count 155 to 160, golden description widened, tests/ layout line updated; MANUAL needed no change — it already named every skill, hook event, and marker key, which is what let the cross-check pass on first run.
