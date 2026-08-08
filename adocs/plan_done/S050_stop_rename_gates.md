id:         S050
goal:       a renamed file does not slip past either Stop gate
accepts:    porcelain rename entries are parsed, so git mv of a completed step into plan_done/ still requires the README and MANUAL stamp, and a rename out of adocs/ still counts as a source change for the recap gate; git mv and mv plus git add -A behave identically, since AGENTS.md section 4 names the first; the README/MANUAL stamp gate gains a test, having survived deletion as the only one of seventeen mutations the suite did not catch; red observed with both rename forms
touches:    bin/moltke.py mode_stop porcelain parsing; tests/test_s005_hooks.py TestStop
excludes:   rename detection in the invariants, which pass --no-renames deliberately
decisions:
closes:     2026-08-07_adversarial.2-F03
blocks:
paused_by:
done:      2026-08-08: both --stop gates read porcelain through one porcelain_paths, splitting a rename on ' -> ' exactly as worktree_state already did, so git mv and mv plus git add -A no longer walk past the README/MANUAL stamp gate; arrival is judged on the index half of the code (A, R, C, plus untracked), so AM and RM count. The recap gate judges a rename by both sides, since a file promoted out of adocs/ adds a source file and one moved in removes one, while a rename staying inside adocs/ is exempt as before. 6 tests, red observed on the three failing shapes, plus the finding's own transcript re-measured: 1 1 1 stamp complaints where it measured 1 0 0, and 1 recap demand where it measured 0. The gate now has tests at all, having survived deletion as the only one of the finding's seventeen mutations. Suite 252 OK, --validate green. README test count 246 to 252; MANUAL's stamp entry names the move shapes it now sees; specs gained a dated note.
