id:         S040
goal:       an audit type cannot write outside adocs/audit/
accepts:    --audit new refuses a type that is not [A-Za-z0-9_-]+, naming the rule, so a path separator cannot escape the directory and a dotted type cannot collide with the .2 namespace S020 reserved for same-day re-runs; the printed path is the real one rather than a lexical relative_to that always looks contained; red observed with '../../outside/pwned', which today creates a stray directory, writes the report outside the glob every check uses, and degrades the finding-id stem to 'pwned'
touches:    bin/moltke.py mode_audit, next_report_path; tests/test_s008_audit.py TestAuditNew
excludes:   validating the audit type against a fixed vocabulary; renaming existing reports
decisions:
closes:     2026-08-07_adversarial-F09
blocks:
paused_by:
done:      2026-08-07: --audit new refuses a type that is not [A-Za-z0-9_-]+, before anything touches the filesystem, so a separator cannot put a report outside the glob every check reads and a dot cannot collide with the same-day re-run suffix. 4 tests plus subtests, red observed. Suite 227 OK, --validate green, and the finding's reproduction re-run. README test count 223 to 227; MANUAL's --audit new row states the rule; the audit skill no longer calls types free-form.
