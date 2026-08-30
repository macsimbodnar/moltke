id:         S174
goal:       init's status step stops contradicting INV-19
accepts:    step 4 item 6 fills status.md only when fresh from the template;
            a kept status.md is left to the ruleset's own status rule (the
            session that changed plan state rewrites it, Parked carried
            forward) — no wording tells init to rewrite an existing file
touches:    skills/init/SKILL.md
excludes:   changing INV-19 itself
closes:     2026-08-29_adversarial.3-F01
author:     Maksym Bodnar
done:       2026-08-30: step 4 item 6 fills status.md only when it is fresh
            from the template (nothing done, nothing in progress, next is
            the first Open entry); a kept status.md is named not this
            skill's to rewrite (INV-19) and left to the ruleset's own status
            rule — the session that changed plan state rewrites the view,
            Parked carried forward. Verified by re-reading step 4 over the
            kept-adocs paths (Detect branches (b)/(d)): no wording directs
            init to rewrite an existing file. README and MANUAL unchanged,
            checked. No suite, per the TESTS rule.
