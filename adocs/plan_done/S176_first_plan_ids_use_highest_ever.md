id:         S176
goal:       first-plan ids use highest-ever-allocated, not next-free-gap
accepts:    step 4 words the id rule as AGENTS.md does — one more than the
            highest ever allocated across the three plan directories, S001
            only when they are empty — so burned gaps are never re-issued
touches:    skills/init/SKILL.md
excludes:   AGENTS.md, which already states the rule
closes:     2026-08-29_adversarial.3-F03
author:     Maksym Bodnar
done:       2026-08-30: step 4 item 4 now words the id rule as AGENTS.md
            does — one more than the highest ever allocated across the
            three plan directories, S001 only when they are empty — and
            names a gap a burned id, never re-issued. Verified against the
            F03 reproduction: over this repository's own plan_done/ (gaps
            at S043, S053, S131, S133, S135, S163) the wording now yields
            the next id above the highest, not S043. README and MANUAL
            unchanged, checked. No suite, per the TESTS rule.
