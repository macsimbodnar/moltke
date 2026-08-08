id:         S057
goal:       the reviewer agent and audit skill state where the fence stops
accepts:    agents/adversarial_reviewer.md and skills/audit/SKILL.md say the fence covers this repository only, so a write to the installed plugin's own source or to a settings file outside the repository is not blocked by it; MANUAL already says this and the two component files contradict it by omission; the statement is one the code supports, traced to mode_pre_write's relative_to boundary
touches:    agents/adversarial_reviewer.md; skills/audit/SKILL.md
excludes:   widening the fence beyond the repository, which S041 recorded as the deliberate boundary
decisions:
closes:     2026-08-07_adversarial.2-F10
blocks:
paused_by:
done:      2026-08-08: agents/adversarial_reviewer.md and skills/audit/SKILL.md now say the fence covers this repository only, naming the two real out-of-repository targets — the installed plugin's own source in the plugin cache and ~/.claude/settings.json — and that --audit check cannot see either, since it reads git status and git diff inside the repository. specs and MANUAL already recorded the boundary; the two files the reviewer actually reads contradicted them by omission. Traced to mode_pre_write returning before the reviewer rule for a path that does not resolve under root, and re-measured: both writes exit 0. 1 test, red observed against the pre-change files. Nothing widened, per the excludes and S041. Suite 266 OK, --validate green. README test count 265 to 266; MANUAL needed no change, since it is the file that was already right.
