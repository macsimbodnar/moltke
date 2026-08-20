id:         S157
goal:       the init skill stops promising a worklog recap gate
accepts:    skills/init/SKILL.md's step 2 lists the gates --stop actually applies,
            with no worklog recap among them; the F08 component-doc scan widens to
            the worklog string so no skill can name it again
touches:    skills/init/SKILL.md, tests/test_2026_08_19_adversarial_findings.py
excludes:   any other rewording of the init skill; the audit skill, done in S148
decisions:
closes:
blocks:
paused_by:
done:      2026-08-20. skills/init/SKILL.md step 2 told a user adopting the workflow that a Stop refuses "source changes with no worklog recap" — a gate that left with the worklog in 0.11.0 (DEC-046), so the one thing the skill says about enforcement named an artifact the tool no longer has. Step 2 now lists what mode_stop actually applies: an invariant violation, a stale status.md, a step that reached plan_done/ without a completion stamp, and a watcher whose result was never taken. The F08 component-doc scan, which read skills/audit/SKILL.md alone and so left this half of the same finding open, is widened to every skills/*/SKILL.md and agents/*.md — the same component_docs() set the flag scan reads. Red observed first: skills/init/SKILL.md:46. README's stated test count was 484 against a 527-test suite; corrected. MANUAL needed nothing: its worklog mention is a changelog line about the removal. Suite 527 OK, --validate green. Noted for a step of its own: skills/step/SKILL.md:42 still says "Note it in the recap", the same era's word with no referent left in that file.
author:    Maksym Bodnar
