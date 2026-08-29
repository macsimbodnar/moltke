id:         S167
goal:       MANUAL and the ruleset agree on the merge-collision renumber
accepts:    either INV-20 and the AGENTS.md never-reuse line state the one
            pre-merge exception MANUAL sanctions, or MANUAL drops the
            sanction; both shipped AGENTS.md copies and specs stay in
            agreement, and the choice is recorded as a decision
touches:    adocs/specs.md; AGENTS.md; templates/AGENTS.md; MANUAL.md
excludes:   any other Teams-section change
closes:     2026-08-29_adversarial-F04
author:     Maksym Bodnar
done:       2026-08-29: the ruleset states the exception rather than MANUAL
            dropping the remedy (DEC-068) — INV-20 and the never-reuse line
            in both AGENTS.md copies now carry the merge-collision renumber
            explicitly, next free id before merging, noted in the merge
            commit. Verified by diffing the two AGENTS.md copies (base
            sections identical again) and re-reading MANUAL's Teams
            paragraph against INV-20: no contradiction remains. README
            unchanged, checked. No suite, per the TESTS rule.
