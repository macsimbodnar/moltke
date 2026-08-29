id:         S165
goal:       init's Detect table covers a moltke AGENTS.md without adocs/
accepts:    the Detect matrix is exhaustive: an existing moltke AGENTS.md with
            adocs/ missing scaffolds only the missing pieces and rewrites only
            the ## Project rules section, so no interview answer is silently
            dropped
touches:    skills/init/SKILL.md
excludes:   the rules skill, which already owns section rewrites
closes:     2026-08-29_adversarial-F02
author:     Maksym Bodnar
done:       2026-08-29: Detect gains the fourth branch — a moltke AGENTS.md
            with adocs/ missing skips the interview (rules already recorded),
            scaffolds only the missing pieces, and points rule changes at
            /moltke:rules' section rewrite. "Neither" became "None of the
            above" so the fall-through stays exhaustive. Verified by
            hand-walking all four states of (AGENTS.md kind x adocs/
            presence) against the table: each now matches exactly one
            branch, and no path re-interviews into a file the scaffold
            refuses to write. README and MANUAL unchanged, checked. No
            suite, per the TESTS rule.
