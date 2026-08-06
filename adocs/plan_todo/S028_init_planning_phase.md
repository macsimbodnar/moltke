id:         S028
goal:       init drives a guided planning phase after scaffolding
accepts:    the init skill's post-scaffold sequence becomes a guided planning session: elicit the prime directive and invariants into specs.md, propose an ordered first plan, create step files via --step new rather than hand-copying the template, record planning-session choices as decisions.md entries, regenerate status.md, end in a commit (AGENTS.md section 4); --session-start in an enabled repo whose specs.md prime directive is still empty after guidance stripping, or whose plan.md lists no steps, says the planning phase is pending and names the file; the nudge disappears once both are filled; it is a nudge in additionalContext, never a blocking exit; red observed against the current scaffold, which stays silent
touches:    skills/init/SKILL.md; bin/moltke.py mode_session_start; tests/test_s005_hooks.py; tests/test_s006_init.py
excludes:   judging plan quality or step granularity; blocking any hook on an unfilled specs.md (DEC-006 no-deadlock); adopting repositories with pre-existing work, which stays a manual exercise (specs non-goal)
decisions:
closes:
blocks:
paused_by:
done:
