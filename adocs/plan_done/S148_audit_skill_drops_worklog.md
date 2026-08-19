id:         S148
goal:       the audit skill stops documenting the removed worklog and --log-prompt
accepts:    skills/audit/SKILL.md documents no worklog and no --log-prompt, and its AGENTS.md section reference reads the section that exists; the dead _turn_exits is gone; the surface golden and its documentation check still pass
touches:    skills/audit/SKILL.md, tests/test_s005_hooks.py _turn_exits and its
            module docstring, tests/test_2026_08_19_adversarial_findings.py
excludes:   any other rewording of the skill
decisions:
closes:     2026-08-19_adversarial-F08
blocks:
paused_by:
done:      2026-08-19 The audit skill's step 3 no longer documents adocs/worklog.md or --log-prompt, both removed in 0.11.0 (DEC-046): an operator following it expected a worklog append among --audit check's expected changes and was told an edit there turns off a Stop recap gate that no longer exists. audit_check has no worklog handling and test_s008_audit.py asserts the opposite of what the skill said. The review-model citation goes from AGENTS.md 10 (Hard prohibitions) to 9. tests/test_s005_hooks.py loses _turn_exits, which called the removed flag from nowhere, and the docstring clause recording that flag's contract, since no test there invokes UserPromptSubmit now. Closes 2026-08-19_adversarial-F08. Red observed first on all four checks; the fifth is the non-vacuity anchor, green before and after, proving the two emptiness scans had something to scan. The section citation is derived from AGENTS.md's own headings, so renumbering the ruleset fails the test rather than misdirecting a reader. Nothing in bin/ changed, so specs' --audit check row and MANUAL's mode row already read correctly; README needed only its test count, 479 to 484. The step file's touches field named bin/moltke.py for _turn_exits, which lives in tests/; corrected in place.
author:    Maksym Bodnar
