id:         S173
goal:       init's first-plan step respects kept files
accepts:    step 4 no longer assumes fresh templates: ids start from the next
            free S<nnn> when plan_todo/ is populated, and status.md is filled
            only when it is fresh from the template — no path directs id
            reuse or overwrites recorded state
touches:    skills/init/SKILL.md
excludes:   the scaffold section
closes:     2026-08-29_adversarial.2-F03
author:     Maksym Bodnar
done:       2026-08-29: step 4 stops assuming fresh templates — the intro
            says fill only what is empty on kept files, step ids come from
            the next free S<nnn> (S001 only when the plan directories are
            empty), and status.md is rewritten to match the plan directories
            rather than blanked. Verified by hand-walking the kept-adocs
            path (Detect branch (b) with an existing populated adocs/): no
            instruction now directs id reuse or overwrites recorded state.
            README and MANUAL unchanged, checked. No suite, per the TESTS
            rule.
