id:         S057
goal:       the reviewer agent and audit skill state where the fence stops
accepts:    agents/adversarial_reviewer.md and skills/audit/SKILL.md say the fence covers this repository only, so a write to the installed plugin's own source or to a settings file outside the repository is not blocked by it; MANUAL already says this and the two component files contradict it by omission; the statement is one the code supports, traced to mode_pre_write's relative_to boundary
touches:    agents/adversarial_reviewer.md; skills/audit/SKILL.md
excludes:   widening the fence beyond the repository, which S041 recorded as the deliberate boundary
decisions:
closes:     2026-08-07_adversarial.2-F10
blocks:
paused_by:
done:
