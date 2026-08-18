id:         S137
goal:       decide whether arm-time watcher enforcement survives the fence retirement
accepts:    a decisions.md entry resolving DEC-049's arm-time lint against DEC-047 (which retired arm-time fences as blockers users route around), chosen by Max from options the agent supplies; whichever way it goes, `--pre-command`, INV-17, AGENTS.md §12 and MANUAL agree with it in one commit, and the 2026-08-18 finding about the lint's bypass is re-read under the outcome
touches:    adocs/decisions.md, adocs/specs.md, AGENTS.md, templates/AGENTS.md, MANUAL.md, and bin/moltke.py only if the lint changes
excludes:   the primitive itself, which is not a blocker and is not in question; bounding a single scan
decisions:  DEC-052
closes:
blocks:     S134
paused_by:
done:
