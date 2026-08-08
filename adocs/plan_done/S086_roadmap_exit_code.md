id:         S086
goal:       --roadmap exits as its documentation says
accepts:    --roadmap exits as its documentation says: specs states exit 0 always and both exit tables reserve 2 for the three hook modes, while an unreadable path returns the backstop's 2; either the mode handles its own failure or the documentation is corrected to match the code, and the exit-code test covers --roadmap; red observed with an unreadable plan tree
touches:    bin/moltke.py mode_roadmap and the main backstop; adocs/specs.md; README.md; MANUAL.md; tests/test_s025_exit_codes.py
excludes:   changing the exit codes of the hook modes
decisions:  
closes:     2026-08-08_adversarial.3-F07
blocks:
paused_by:
done:      2026-08-08: --roadmap handles its own read failure and exits 0, which is what specs and both exit tables already said. It was dispatched inside the main try and returned the backstop 2 — the same defect .2-F10 reported for --audit, in its twin — and AGENTS.md tells every agent to run this mode at the end of a unit of work, so a wrapper reading 2 as blocked got a block from a mode documented as never blocking. 2 tests, red observed. Suite 376 OK, --validate green. README test count 370 to 376; MANUAL and the specs table already said exit 0 and now that is true; specs gained a dated note covering this and S087.
