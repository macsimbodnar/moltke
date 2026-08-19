id:         S151
goal:       the reviewer fence refuses overwriting another report and permits correcting its own new test
accepts:    a reviewer write to an existing file under adocs/audit/ that is not the report named by the current baseline is refused, and a write to a tests/ file the same run created is permitted; both decided from moltke_audit_baseline.json; red observed first on each direction
touches:    bin/moltke.py mode_pre_write reviewer branch, the audit baseline read
excludes:   fencing Bash, which DEC-022 accepted as unpoliced
decisions:
closes:     2026-08-19_adversarial-F11
blocks:
paused_by:
done:
