id:         S037
goal:       the Stop recap gate stops treating .claude-plugin/ as not-source
accepts:    a change to .claude-plugin/plugin.json requires a recap like any other source file, while .claude/settings.json stays exempt; the exempt prefixes are listed explicitly with their separators rather than sharing a stem, so .clauderc and any future .claude* file at the root are not exempt by accident; a table-driven test walks representative paths and asserts block-or-allow for each; red observed with the measured table in the finding, where .claude-plugin/plugin.json and .claudefoo both allow
touches:    bin/moltke.py mode_stop changed_source; tests/test_s005_hooks.py TestStop
excludes:   changing which paths under adocs/ are exempt
decisions:
closes:     2026-08-07_adversarial-F06
blocks:
paused_by:
done:      2026-08-07: the recap gate exempts adocs/ and .claude/ by directory with their separators, listed in RECAP_EXEMPT, so the plugin manifest and any .claude* file at the root are source again. 1 table-driven test over nine paths, red observed on three rows. Suite 213 OK, --validate green, and the finding's own table re-measured with the two wrong rows flipped. README test count 212 to 213; MANUAL's recap-gate entry now states what source means and what the bare prefix used to exempt.
