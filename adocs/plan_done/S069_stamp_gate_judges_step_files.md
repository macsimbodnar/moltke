id:         S069
goal:       the stamp gate judges step files, not every path under plan_done/
accepts:    the Stop stamp gate judges step files by name rather than every path under plan_done/, so --scaffold's own .gitkeep in a repository that already has commits does not block every turn with a completion complaint about a file that is not a step; a real step file arriving unstamped still blocks; red observed with the scaffold-into-committed-repo fixture, where staging does not clear it and only a commit does
touches:    bin/moltke.py mode_stop stamp gate; tests/test_s005_hooks.py
excludes:   changing what --scaffold writes
decisions:  
closes:     2026-08-08_adversarial.2-F03
blocks:
paused_by:
done:      2026-08-08: the Stop stamp gate judges step files, matching STEP_FILE_RE like plan_steps does. It tested the porcelain status and the path prefix alone, so anything arriving under plan_done/ was asked for a completion stamp — including --scaffold's own .gitkeep, which meant every Stop blocked in a project with history the moment it adopted moltke, with staging not clearing it and --validate green throughout. This was the only reader of plan_done/ without that filter, which is why INV-5 and INV-6 said nothing about the same file. 3 tests, red observed on three stray filenames and on the scaffold path itself. Suite 329 OK, --validate green. README test count 326 to 329; MANUAL already said 'it sees the step arrive', which is now true; specs gained a dated note.
