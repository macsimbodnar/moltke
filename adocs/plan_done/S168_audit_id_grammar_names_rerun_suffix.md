id:         S168
goal:       the audit id grammar can express its own re-run suffix
accepts:    the audit skill and INV-20 both name the optional run suffix —
            YYYY-MM-DD_<type>[.N]-F<nn>, type [A-Za-z0-9_-]+ — so the four
            tracked .2 reports parse under the stated grammar
touches:    skills/audit/SKILL.md; adocs/specs.md
excludes:   renaming any existing report
closes:     2026-08-29_adversarial-F05
author:     Maksym Bodnar
done:       2026-08-29: both statements of the grammar carry the optional run
            suffix — the audit skill names the report
            YYYY-MM-DD_<type>[.N].md and INV-20 the finding id
            YYYY-MM-DD_<type>[.N]-F<nn>, type [A-Za-z0-9_-]+. Verified by
            parsing the four tracked .2 report names and their finding ids
            against the new grammar by eye: all fit; no report renamed.
            README and MANUAL unchanged, checked. No suite, per the TESTS
            rule.
