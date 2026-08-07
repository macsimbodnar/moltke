id:         S050
goal:       a renamed file does not slip past either Stop gate
accepts:    porcelain rename entries are parsed, so git mv of a completed step into plan_done/ still requires the README and MANUAL stamp, and a rename out of adocs/ still counts as a source change for the recap gate; git mv and mv plus git add -A behave identically, since AGENTS.md section 4 names the first; the README/MANUAL stamp gate gains a test, having survived deletion as the only one of seventeen mutations the suite did not catch; red observed with both rename forms
touches:    bin/moltke.py mode_stop porcelain parsing; tests/test_s005_hooks.py TestStop
excludes:   rename detection in the invariants, which pass --no-renames deliberately
decisions:
closes:     2026-08-07_adversarial.2-F03
blocks:
paused_by:
done:
