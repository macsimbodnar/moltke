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
done:      2026-08-11: review has three tiers (DEC-044). Tier 1, a fast check after every --step done — one small subagent over the completion commit's diff, top real problems only, no report file, no finding ids, routed by rules that already exist: trivial fixed under §4, real becomes a step, nothing is one console line. Tier 2, the agent proposes a full audit on real risk and the user accepts or postpones, a postponed proposal parking as one status.md line. Tier 3, /moltke:audit on demand with its teeth intact: clean-context spawn, report before fix, every finding homed (INV-10 unchanged), closure by re-run or by recorded decision with DEC-041 as precedent. The reviewer fence is untouched and binds only audit runs, which are consent-based now, so nothing about it is mandatory. AGENTS.md §10 rewritten, template byte-identical, skills/step and skills/audit carry their halves, MANUAL gained the Review model section. No code changed, so no new tests; the drift, template-generic and surface suites hold the documents. Suite 438 OK, --validate green. README checked, no change.
