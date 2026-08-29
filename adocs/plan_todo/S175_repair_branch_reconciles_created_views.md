id:         S175
goal:       the repair branch reconciles view files it creates
accepts:    when Detect branch (a) creates a missing status.md or plan.md,
            the file is brought to match the plan directories before it is
            read back to the user — no template-fresh view over a populated
            plan history
touches:    skills/init/SKILL.md
excludes:   the fresh-scaffold path
closes:     2026-08-29_adversarial.3-F02
author:
done:
