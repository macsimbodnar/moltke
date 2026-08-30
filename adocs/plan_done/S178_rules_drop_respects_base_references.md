id:         S178
goal:       rules Drop points catalog topics at their none option
accepts:    the rules skill directs Drop away from removing a catalog topic
            the base ruleset references (PLAN, TESTS, DOCS, COMMITS,
            REVIEW): those change to their none/off option instead; only
            non-catalog lines can be removed outright
touches:    skills/rules/SKILL.md
excludes:   the catalog itself
closes:     2026-08-29_adversarial.3-F07
author:     Maksym Bodnar
done:       2026-08-30: the rules skill's Drop is now non-catalog ids only —
            catalog topics are changed, never dropped, with turning one off
            a Change to its none/off option — because the base ruleset
            reads PLAN, TESTS, DOCS, REVIEW, and COMMITS by id and a
            dropped line would leave it referencing an undefined rule.
            Verified against the F07 reproduction: Drop on TESTS is now
            directed to the catalog's none line instead of deletion, so the
            finish gate stays evaluable. README and MANUAL unchanged,
            checked. No suite, per the TESTS rule.
