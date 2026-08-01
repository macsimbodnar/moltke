id:         S008
goal:       adversarial_reviewer subagent and project_audit skill
accepts:    reviewer runs with read tools plus write access limited to project/audit/ and cannot edit source; the report is written before any fix, with per-finding ids and severities; findings map one-to-one to plan steps carrying closes: links or to decisions with a stated reason; re-running the audit is what moves a finding to closed
touches:    agents/adversarial_reviewer.md, skills/project_audit/
done:
