id:         S020
goal:       an audit can be re-run the same day
accepts:    a second --audit new of the same type on the same date creates a suffixed report rather than refusing; finding ids still carry their own report's stem so INV-10 holds; an existing report is still never overwritten
touches:    bin/moltke.py audit_new; tests/test_s008_audit.py
excludes:   changing the report naming scheme for the first run of a day
decisions:
closes:     2026-08-06_adversarial-F09
blocks:
paused_by:
done:      2026-08-06: --audit new takes a .2/.3 sequence suffix on a same-day re-run and still never overwrites; INV-10's stem check tightened from startswith to an exact <stem>-F<nn> match, which the suffix made necessary. 4 tests, red observed. Suite 145 OK, --validate green. README test count 142 to 145; MANUAL --audit new row updated; AGENTS.md section 10 and templates/AGENTS.md changed identically; skills/audit/SKILL.md steps 1 and 5 no longer say to wait for tomorrow.
