id:         S172
goal:       re-running init repairs unwired entry points and missing scaffold
accepts:    Detect branch (a) — already set up — still checks the entry-point
            wiring and the scaffold list, offers to wire or create what is
            missing, and only then stops; a 1.0.0-initialised repo with an
            unwired CLAUDE.md is repaired by a second /moltke:init run
touches:    skills/init/SKILL.md
excludes:   any change to the interview or the rules recording
closes:     2026-08-29_adversarial.2-F02
author:     Maksym Bodnar
done:       2026-08-29: Detect branch (a) checks the repair cases before it
            stops — unwired entry points get the step 3 wiring offer,
            missing scaffold-list files get the offer to create them.
            Verified by hand-walking a 1.0.0-initialised repo with an
            unwired CLAUDE.md: branch (a) matches, the wiring offer now
            fires before the stop. README and MANUAL unchanged, checked.
            No suite, per the TESTS rule.
