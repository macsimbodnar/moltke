id:         S160
goal:       replace the enforcement product with the v1 rules product
accepts:    the plugin ships no executable code; init interviews the user and
            records Project rules in AGENTS.md; the rules and audit skills are
            coherent with the new ruleset; templates scaffold a repository that
            works by hand; README and MANUAL describe v1; this repository's own
            adocs say v1
touches:    everything — bin, hooks, tests, skills, agents, templates, docs,
            adocs
excludes:   the 1.0.0 release to the config roots (S161); re-running init on
            this repository interactively
decisions:  DEC-062, DEC-063
author:     Maksym Bodnar
done:       2026-08-23: the plugin is markdown only. Deleted: bin/, hooks/,
            tests/, the step skill, the marker, the merge attributes, the
            testing ledger (DEC-062). init interviews over the nine-topic
            catalog and records Project rules in AGENTS.md (DEC-063); rules
            is new; audit keeps the cold reviewer and the evidence-first
            order without baselines or fences. Verified by hand-following
            the init skill in a scratch repository: scaffold from templates,
            defaults recorded, a step moved todo -> current -> done by hand.
            A living-files sweep found one stale enforcement claim left
            (marketplace.json plugin description), fixed. README and MANUAL
            rewritten this step, so checked. No suite, per the TESTS rule —
            this stamp is the record of what was verified instead.
