id:         S108
goal:       review has three tiers: fast check by habit, full audit by consent
accepts:    AGENTS.md §10 describes the three tiers. Tier 1: after each completed
            step, a fast check — one small subagent over that step's diff, top
            real problems only, no report file, no finding ids; trivial findings
            fixed under §4's trivial-in-scope rule, real ones become steps, none
            means one console line. Tier 2: the agent proposes a full adversarial
            audit when risk warrants it, with examples; the user accepts or
            postpones; a postponed proposal is one line in status.md's Parked
            block so it survives sessions without nagging. Tier 3: /moltke:audit
            on user demand, always available, unchanged in mechanics.
            When a full audit runs, its rules keep their teeth: clean-context
            spawn, report before fix, every finding gets a step or a decision
            (INV-10 unchanged). Closure softens: a finding closes on a re-run
            that no longer reports it, or by a recorded decision — DEC-041 is the
            precedent and is cited.
            skills/step/SKILL.md carries the fast check in its completion flow;
            skills/audit/SKILL.md carries the proposal etiquette and the softened
            closure rule; MANUAL.md describes the model in a short section.
            The reviewer write fence is untouched: it binds only audit runs,
            which are now consent-based, so nothing about it is mandatory.
touches:    AGENTS.md §10; templates/AGENTS.md; skills/step/SKILL.md;
            skills/audit/SKILL.md; MANUAL.md; adocs/decisions.md (DEC-044)
excludes:   changing bin/moltke.py --audit mechanics; the reviewer fence;
            retroactively closing the seven planned 2026-08-09 findings
decisions:  DEC-044
closes:
blocks:
paused_by:
done:
