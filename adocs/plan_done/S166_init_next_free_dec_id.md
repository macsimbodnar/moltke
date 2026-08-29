id:         S166
goal:       init records adoption under the next free DEC id, not always DEC-001
accepts:    the skill words the adoption entry as the migration prompt does:
            next free DEC-<nnn>, DEC-001 only when decisions.md is fresh from
            the template
touches:    skills/init/SKILL.md
excludes:   any change to the decisions.md template
closes:     2026-08-29_adversarial-F03
author:     Maksym Bodnar
done:       2026-08-29: the adoption entry is worded as the migration prompt
            already words it — next free DEC-<nnn>, DEC-001 only when
            decisions.md is fresh from the template, "ids are never reused"
            stated in place. Verified by re-reading the section against the
            two pre-existing-ledger paths (Detect append branch, partial
            state branch): neither can now be told to mint a duplicate
            DEC-001. README and MANUAL unchanged, checked. No suite, per
            the TESTS rule.
