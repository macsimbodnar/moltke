id:         S056
goal:       the worklog exemption does not hand the reviewer a silent channel
accepts:    an append to adocs/worklog.md made by the reviewer rather than by the hook is not silently expected, and does not let a recap heading appear that discharges the Stop gate for work the reviewer did; the shape-based exemption S036 introduced is narrowed or corroborated, for instance against the prompts the hook actually logged during the run; a genuine hook append is still expected, since undoing that would restore the false positive on every audit that F05 was about
touches:    bin/moltke.py worklog_only_grew and audit_check; tests/test_s008_audit.py
excludes:   fencing Bash, which DEC-022 settled against; reverting S036
decisions:
closes:     2026-08-07_adversarial.2-F09
blocks:
paused_by:
done:      2026-08-08: --audit check reads the worklog append instead of only testing its shape. --log-prompt writes a '## <stamp> prompt' heading and the prompt quoted line by line, so an appended region holding anything else is unexpected and exits 1, while a genuine hook append stays expected and is named in the listing rather than passing unmentioned. Quoting is what makes this safe: a prompt containing a recap heading or a fence arrives prefixed '> '. S036's false positive stays fixed, verified by its four tests unchanged. Residual stated in specs and MANUAL: Stop cannot tell who appended a recap and still accepts one in the moment, so --audit check is where the fabrication surfaces — DEC-022's prevention-to-detection trade applied to this file. 4 tests, red observed, plus the finding's transcript re-measured. Suite 265 OK, --validate green. README test count 261 to 265; MANUAL's audit-check paragraph and skills/audit/SKILL.md both corrected, the latter having contradicted the code since S036.
