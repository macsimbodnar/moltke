id:         S017
goal:       --audit check reconciles what an audit changed
accepts:    --audit new records a working-tree baseline; --audit check prints expected and unexpected changes and exits 1 when anything is unexpected; a new file under tests/ and this run's own report are expected; a modified existing test is unexpected; the check is correct from a dirty starting tree; the fence permits Write under adocs/audit/ and new files under tests/ and still blocks elsewhere; specs, MANUAL, the reviewer agent and the audit skill no longer claim Bash is fenced; golden refreshed with --audit check documented in specs and MANUAL in this same commit
touches:    bin/moltke.py audit_new, new audit_check, AUDIT_OPS, mode_pre_write; skills/audit/SKILL.md; agents/adversarial_reviewer.md; adocs/specs.md; MANUAL.md; tests/golden/cli_surface.txt; tests/test_s008_audit.py
excludes:   Bash command-string inspection, rejected as unparseable; blocking the reviewer's Bash writes at all; reverting to prevention
decisions:  DEC-022
closes:     2026-08-06_adversarial-F03
blocks:
paused_by:
done:      2026-08-06: --audit new records a baseline, --audit check reconciles the run; fence widened to new files under tests/. 11 tests in test_s008_audit.py, red observed. Golden refreshed with check documented in specs and MANUAL in this commit. Suite 132 OK, --validate green. README updated: test count 121 to 132, reviewer line, audit gate commands; MANUAL gained the --audit check row and its git-visibility limits, and the fence entry now lists three residual limits. F03 stays planned until S027 re-runs the audit.
