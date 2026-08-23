id:         S162
goal:       keep the 0.x -> 1.0 migration prompt in the repo's memory
accepts:    adocs/migration_prompt.md carries the machine update order and a
            paste-ready agent prompt for repository cleanup and
            re-initialization, free of machine-specific paths; the shipped
            documentation is unchanged — Max wants a copy-paste note that
            travels in git, not a product doc
touches:    adocs only
excludes:   any change to skills, templates, README, or MANUAL
author:     Maksym Bodnar
done:       2026-08-23: adocs/migration_prompt.md holds both layers — the
            per-root plugin update with its point-of-no-return warning, and
            the agent prompt with <MOLTKE_TEMPLATES> as a placeholder instead
            of this machine's checkout path. First drafted as a root
            MIGRATION.md referenced from MANUAL and README; Max redirected
            mid-step (operator note, not product doc, DEC-064), so those
            edits were reverted before any commit. The first completion
            commit carried this file with the pre-redirect fields — a
            replace with no assert silently no-op'd — and the fast check
            caught it plus three prompt gaps (missing
            .git/moltke_audit_baseline.json cleanup, surface_guard not
            harvested); all fixed by amending the unpushed commit. Verified
            by re-reading this file from the tree and proofreading the
            prompt against the S160 migration mapping; no suite, per the
            TESTS rule.
