id:         S164
goal:       init wires the ruleset into an existing CLAUDE.md
accepts:    when CLAUDE.md exists without an @AGENTS.md reference, init
            offers to append that one line (append, never overwrite, INV-19
            intact) and reports what it did; same offer for an existing
            .cursor/rules/moltke.mdc
touches:    skills/init/SKILL.md
excludes:   any change to scaffold behaviour for files init creates fresh
closes:     2026-08-29_adversarial-F01
author:
done:
