id:         S027
goal:       bump 0.3.0, re-run the audit, close findings
accepts:    plugin.json is 0.3.0; the audit is re-run with S020's same-day suffix; every finding that no longer reproduces is closed; findings that only reproduce against a live install stay planned with a note saying so; --audit list exits 0; status.md regenerated
touches:    .claude-plugin/plugin.json; adocs/audit/; adocs/status.md
excludes:   fixing anything newly found, which becomes its own step; the live install verification, which is Max's under DEC-014
decisions:  DEC-002
closes:
blocks:
paused_by:
done:      2026-08-07: 0.3.0 bumped and manifest re-validated; audit re-run as adocs/audit/2026-08-07_adversarial.md with a verdict on all fourteen prior findings decided against the code. Twelve closed, F03 accepted under DEC-022, F02 held planned because the installed plugin is still 0.2.0 at 1064774. Eleven new findings, four high, each mapped to one of S032..S042 and ordered ahead of the feature work; S044 added as the next closure run. --audit list exits 0. README and MANUAL checked: no change needed, the version number lives in plugin.json and both documents already describe it as the thing that gates updates. Date rolled past midnight so the re-run took a new date rather than S020's same-day suffix.
