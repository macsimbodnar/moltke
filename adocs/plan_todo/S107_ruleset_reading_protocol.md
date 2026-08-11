id:         S107
goal:       the ruleset tells agents to look up, not to read everything
accepts:    AGENTS.md §1 is a tiered protocol: a routine turn starts from the
            SessionStart context alone with zero document reads; status.md and
            plan.md are read whole when orientation is needed (both small);
            specs.md is read whole only because S106 made it small; decisions.md
            is entered through its index and grepped by id or tag, never read
            whole. The precedence chain is stated: .moltke.local.md (machine) >
            the Project rules section (project) > the base ruleset — naming the
            two override surfaces that S109 and S110 implement.
            §2's write modes match S105/S106 reality: decisions.md compact-freely
            with stable ids, worklog trimmable, plan.md pruned by --step done.
            §7's dated-note rule is replaced: behaviour changes update the current
            wording in specs.md; the narrative lives in the step file and the
            commit message.
            §8 drops the append-only ceremony: supersede by rewrite or delete,
            ids stable, the why kept to a line.
            §11 drops the decisions.md prohibition; the plan_done/ and git
            prohibitions stay.
            One line states subagents may be spawned freely whenever useful,
            never required, never forbidden, and no other sentence in the ruleset
            constrains agent spawning — verified by survey.
            templates/AGENTS.md carries the identical ruleset; the template
            parity and generic-content tests stay green.
touches:    AGENTS.md; templates/AGENTS.md
excludes:   §10, which is S108's job; creating the two override surfaces, which
            are S109 and S110; any code change
decisions:  DEC-042
closes:
blocks:
paused_by:
done:
