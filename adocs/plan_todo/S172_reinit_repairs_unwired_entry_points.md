id:         S172
goal:       re-running init repairs unwired entry points and missing scaffold
accepts:    Detect branch (a) — already set up — still checks the entry-point
            wiring and the scaffold list, offers to wire or create what is
            missing, and only then stops; a 1.0.0-initialised repo with an
            unwired CLAUDE.md is repaired by a second /moltke:init run
touches:    skills/init/SKILL.md
excludes:   any change to the interview or the rules recording
closes:     2026-08-29_adversarial.2-F02
author:
done:
