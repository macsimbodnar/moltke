id:         S174
goal:       init's status step stops contradicting INV-19
accepts:    step 4 item 6 fills status.md only when fresh from the template;
            a kept status.md is left to the ruleset's own status rule (the
            session that changed plan state rewrites it, Parked carried
            forward) — no wording tells init to rewrite an existing file
touches:    skills/init/SKILL.md
excludes:   changing INV-19 itself
closes:     2026-08-29_adversarial.3-F01
author:
done:
