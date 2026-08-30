id:         S175
goal:       the repair branch reconciles view files it creates
accepts:    when Detect branch (a) creates a missing status.md or plan.md,
            the file is brought to match the plan directories before it is
            read back to the user — no template-fresh view over a populated
            plan history
touches:    skills/init/SKILL.md
excludes:   the fresh-scaffold path
closes:     2026-08-29_adversarial.3-F02
author:     Maksym Bodnar
done:       2026-08-30: Detect branch (a) now says a status.md or plan.md it
            creates starts template-fresh over real history and is brought
            to match the plan directories before the read-back — status.md's
            view fields from the three directories, plan.md's Open list one
            entry per open step file, with order and the description
            paragraph proposed for the user to correct since the lost file
            was their only holder. Verified by re-walking branch (a) over
            the F02 reproduction (set-up repository missing status.md or
            plan.md): the read-back no longer shows a template-fresh view.
            README and MANUAL unchanged, checked. No suite, per the TESTS
            rule.
