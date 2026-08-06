id:         S019
goal:       fenced guidance never discharges a finding
accepts:    a finding id appearing only inside a fenced block or HTML comment in decisions.md no longer satisfies INV-10; a real entry still does; red observed with the baseline violation established first, as the audit report reproduced it
touches:    bin/moltke.py finding_references; tests/test_s008_audit.py
excludes:   requiring the reference to sit in a specific field of the entry, which is a separate tightening
decisions:
closes:     2026-08-06_adversarial-F05
blocks:
paused_by:
done:
