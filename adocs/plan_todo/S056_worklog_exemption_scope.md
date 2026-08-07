id:         S056
goal:       the worklog exemption does not hand the reviewer a silent channel
accepts:    an append to adocs/worklog.md made by the reviewer rather than by the hook is not silently expected, and does not let a recap heading appear that discharges the Stop gate for work the reviewer did; the shape-based exemption S036 introduced is narrowed or corroborated, for instance against the prompts the hook actually logged during the run; a genuine hook append is still expected, since undoing that would restore the false positive on every audit that F05 was about
touches:    bin/moltke.py worklog_only_grew and audit_check; tests/test_s008_audit.py
excludes:   fencing Bash, which DEC-022 settled against; reverting S036
decisions:
closes:     2026-08-07_adversarial.2-F09
blocks:
paused_by:
done:
