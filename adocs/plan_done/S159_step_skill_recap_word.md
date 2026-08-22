id:         S159
goal:       the step skill stops pointing a drive-by fix at the recap
accepts:    skills/step/SKILL.md's "trivial and in scope" routing names a place
            that exists — the step stamp and the commit message, AGENTS.md §7's
            own wording — with no recap among them; a component-doc scan refuses
            the recap named as a destination, so no shipped skill can direct a
            write at it again; the bare word stays legal, since the console
            recap is live at decision level (DEC-037, DEC-038, DEC-046)
touches:    skills/step/SKILL.md, tests/test_2026_08_19_adversarial_findings.py
excludes:   every other line of the step skill; whether AGENTS.md should restate
            the console recap it no longer mentions
decisions:
closes:
blocks:
paused_by:
done:      2026-08-22. skills/step/SKILL.md:42 told an agent to note a trivial in-scope fix "in the recap" — the worklog era's word for a place DEC-046 deleted in 0.11.0, in a file that says stamp everywhere else, so the one instruction for recording a drive-by fix pointed at nothing. It now says the step stamp and the commit message, which is AGENTS.md §7's own wording for where a step's narrative lives. The guard is a new scan in TestComponentDocsNameOnlyWhatExists over the same component_docs() set as the worklog scan, and it refuses the recap named as a destination — (in|into|to|under) the recap — not the bare word, since DEC-037 and DEC-038 put a short recap in the console and DEC-046 kept it there, so a skill may still correctly name one. The whole text is searched rather than each line, because \s+ spans the wrap this repository's prose puts mid-phrase, and the pattern is asserted against both the removed phrasing and a wrapped copy so a regex that stopped matching cannot pass as a clean scan. Red observed first: skills/step/SKILL.md:42. README's stated test count was 527 against a 540-test suite — S158 completed at 538 and left the line alone; corrected. MANUAL needed nothing: its review-model line gives the same routing without naming a record. No behaviour changed, so specs.md needed nothing. Suite 540 OK, --validate green.
author:    Maksym Bodnar
