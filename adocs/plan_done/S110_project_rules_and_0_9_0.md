id:         S110
goal:       a project-rules override section, and 0.9.0 ships the batch
accepts:    templates/AGENTS.md ends with a "## Project rules" section whose
            guidance comment says rules written there override the base ruleset
            above for that repository; AGENTS.md here carries the same section;
            the template-generic tests stay green (no DEC ids, no
            project-specific content in the template).
            The precedence chain §1 already states is now fully real:
            .moltke.local.md exists (S109), the Project rules section exists
            (this step).
            MANUAL.md documents the section next to the local file.
            .claude-plugin/plugin.json reads 0.9.0 and the golden plugin test
            passes, so one install carries S105 through S110.
            The full suite and --validate are green at the bumped commit, and the
            recap records the final measured always-read set against the ~180 KB
            starting point.
touches:    templates/AGENTS.md; AGENTS.md; MANUAL.md; .claude-plugin/plugin.json
excludes:   any enforcement of what the section may contain; re-running the
            audit, which stays governed by DEC-041 and the S108 model
decisions:  DEC-043
closes:
blocks:
paused_by:
done:      2026-08-11: the Project rules override section lands in AGENTS.md and its template, byte-identical and generic — rules there override the base ruleset for that repository and travel in git, while .moltke.local.md overrides both per machine, the chain §1 states and MANUAL now documents. plugin.json bumped 0.9.0 so one install ships S105 through S110: INV-8 retirement, plan pruning, the compacted documents, the reading protocol, the three-tier review model, and the two override surfaces. Always-read set measured at completion: ~51 KB against 180,518 bytes at e22a911, with per-step growth approximately zero by construction. Suite 444 OK, --validate green. README checked, no change — the test count already reads 444; MANUAL gained the precedence paragraph alongside the local-file section.
