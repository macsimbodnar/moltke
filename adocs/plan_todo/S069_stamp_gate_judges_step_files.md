id:         S069
goal:       the stamp gate judges step files, not every path under plan_done/
accepts:    the Stop stamp gate judges step files by name rather than every path under plan_done/, so --scaffold's own .gitkeep in a repository that already has commits does not block every turn with a completion complaint about a file that is not a step; a real step file arriving unstamped still blocks; red observed with the scaffold-into-committed-repo fixture, where staging does not clear it and only a commit does
touches:    bin/moltke.py mode_stop stamp gate; tests/test_s005_hooks.py
excludes:   changing what --scaffold writes
decisions:  
closes:     2026-08-08_adversarial.2-F03
blocks:
paused_by:
done:
