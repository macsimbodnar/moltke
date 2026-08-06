id:         S020
goal:       an audit can be re-run the same day
accepts:    a second --audit new of the same type on the same date creates a suffixed report rather than refusing; finding ids still carry their own report's stem so INV-10 holds; an existing report is still never overwritten
touches:    bin/moltke.py audit_new; tests/test_s008_audit.py
excludes:   changing the report naming scheme for the first run of a day
decisions:
closes:     2026-08-06_adversarial-F09
blocks:
paused_by:
done:
