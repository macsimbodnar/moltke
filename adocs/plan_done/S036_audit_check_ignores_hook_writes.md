id:         S036
goal:       --audit check does not blame the plugin's own worklog writes on the reviewer
accepts:    a worklog change made while the audit ran is not reported as unexpected, because UserPromptSubmit appends to it on every prompt and the reviewer never touches it; reproduced live on this repository during the S027 run, where the only unexpected entry was adocs/worklog.md; a reviewer that genuinely rewrites the worklog is still reported, so the exemption is scoped to appends rather than to the path
touches:    bin/moltke.py audit_check; tests/test_s008_audit.py TestAuditReconciliation; MANUAL.md
excludes:   exempting the rest of adocs/, which the reviewer must not touch
decisions:
closes:     2026-08-07_adversarial-F05
blocks:
paused_by:
done:      2026-08-07: --audit new records the worklog's length and hash, and --audit check treats a worklog change as expected only while the file still starts with those bytes, on the working-tree and the committed side alike. 4 tests, red observed as the finding's own false positive. Suite 217 OK, --validate green, and the finding's isolation sequence re-measured. README test count 213 to 217; MANUAL's --audit check entry now explains the worklog exemption and its limit.
