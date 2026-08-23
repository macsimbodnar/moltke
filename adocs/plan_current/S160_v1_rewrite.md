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
done:
