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
done:      2026-08-11: the ruleset tells agents to look up, not to read everything. §1 is a tiered protocol — routine turns start from the SessionStart injection with zero document reads, status.md and plan.md read whole for orientation, specs.md read whole because S106 made it small, decisions.md entered through its index and grepped, never read whole — and states the precedence chain: .moltke.local.md over the Project rules section over the base ruleset, the two surfaces S109 and S110 implement. §2, §4, §7, §8, §9 and §11 now match S105/S106 reality: specs holds current wording with the narrative in step stamps and commits, plan.md prunes, decisions.md compacts freely with stable ids and its prohibition is dropped from §11 while the plan_done/ and git prohibitions stay. One permission line says subagents spawn freely, never required, never forbidden; the survey found no constraining sentence — the two remaining spawn mentions enable audits or are the stack metaphor. templates/AGENTS.md is byte-identical, drift test green. Suite 438 OK, --validate green. README checked, no change; MANUAL checked, no change — §1 is agent-facing and MANUAL's daily-use section already describes the hooks, not the reading order.
