id:         S173
goal:       init's first-plan step respects kept files
accepts:    step 4 no longer assumes fresh templates: ids start from the next
            free S<nnn> when plan_todo/ is populated, and status.md is filled
            only when it is fresh from the template — no path directs id
            reuse or overwrites recorded state
touches:    skills/init/SKILL.md
excludes:   the scaffold section
closes:     2026-08-29_adversarial.2-F03
author:
done:
