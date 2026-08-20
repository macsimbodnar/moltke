id:         S153
goal:       the self-host checks name what they check, and the audit commit shape is stated
accepts:    the two self-host checks live in a class named for what they check, and either say in the failure message that untriaged findings are an expected transient or are scoped to the invariants they mean; the audit skill states that a report and the steps closing its findings land in one commit; red observed first
touches:    tests/test_s007_step.py, tests/test_s003_invariants.py, skills/audit/SKILL.md
excludes:   relaxing INV-10 itself
decisions:
closes:     2026-08-19_adversarial-F13
blocks:
paused_by:
done:      2026-08-20: both self-host --validate anchors moved into TestThisRepositoryPassesValidate in tests/test_s003_invariants.py and tests/test_s007_step.py, with a failure message naming untriaged audit findings (INV-10) as the expected transient between a report and its triage. Red observed first on a scratch copy of this repository carrying one untriaged open finding: the two anchors failed under the names of the rules they anchored, saying nothing about audits. skills/audit/SKILL.md step 4 and MANUAL's Review model now state that the report, the steps closing its findings, and any decision entries land in one commit. The green-commit rule cites AGENTS.md's Git section by name because the skill-citation guard admits only the review section's number. Suite green, 511 tests. README and MANUAL checked; MANUAL changed, README already said --audit list refuses while a finding has no home.
author:    Maksym Bodnar
