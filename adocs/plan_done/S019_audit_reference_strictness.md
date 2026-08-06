id:         S019
goal:       fenced guidance never discharges a finding
accepts:    a finding id appearing only inside a fenced block or HTML comment in decisions.md no longer satisfies INV-10; a real entry still does; red observed with the baseline violation established first, as the audit report reproduced it
touches:    bin/moltke.py finding_references; tests/test_s008_audit.py
excludes:   requiring the reference to sit in a specific field of the entry, which is a separate tightening
decisions:
closes:     2026-08-06_adversarial-F05
blocks:
paused_by:
done:      2026-08-06: finding_references reads decisions.md through strip_guidance like every other scanner. 4 tests in test_s008_audit.py, red observed as 'moltke: all checks pass' with the baseline violation established first. Suite 142 OK, --validate green, --audit list still attributes all 14 findings. README test count 138 to 142; MANUAL checked, no change needed — it never described how a finding gets discharged. specs gained a dated note recording that the universal strip_guidance rule had one exception until now, the fifth appearance of this defect.
