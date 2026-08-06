id:         S027
goal:       bump 0.3.0, re-run the audit, close findings
accepts:    plugin.json is 0.3.0; the audit is re-run with S020's same-day suffix; every finding that no longer reproduces is closed; findings that only reproduce against a live install stay planned with a note saying so; --audit list exits 0; status.md regenerated
touches:    .claude-plugin/plugin.json; adocs/audit/; adocs/status.md
excludes:   fixing anything newly found, which becomes its own step; the live install verification, which is Max's under DEC-014
decisions:  DEC-002
closes:
blocks:
paused_by:
done:
