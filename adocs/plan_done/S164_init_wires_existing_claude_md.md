id:         S164
goal:       init wires the ruleset into an existing CLAUDE.md
accepts:    when CLAUDE.md exists without an @AGENTS.md reference, init
            offers to append that one line (append, never overwrite, INV-19
            intact) and reports what it did; same offer for an existing
            .cursor/rules/moltke.mdc
touches:    skills/init/SKILL.md
excludes:   any change to scaffold behaviour for files init creates fresh
closes:     2026-08-29_adversarial-F01
author:     Maksym Bodnar
done:       2026-08-29: scaffold gains an entry-point wiring paragraph — an
            existing CLAUDE.md without an @AGENTS.md reference, or a
            .cursor/rules/moltke.mdc that does not reference the ruleset,
            gets the offer to append one line, reported as wired rather than
            kept; append only, INV-19 intact. Verified by hand-walking the
            established-repo scenario against the new text: Detect falls
            through (no AGENTS.md), interview runs, scaffold creates
            AGENTS.md, the kept CLAUDE.md now triggers the wire offer.
            README and MANUAL describe init at one remove and needed no
            change. No suite, per the TESTS rule.
