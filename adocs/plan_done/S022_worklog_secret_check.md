id:         S022
goal:       worklog secret-shape check runs in the suite
accepts:    the suite fails when a prefixed key shape or a PEM private-key header appears in adocs/worklog.md; the test first asserts a known-bad fixture string is caught and fails if it is not, so it is non-vacuous by construction; git shas and other 40-hex strings never trip it; MANUAL records the leak exposure and the escape procedure for a real one
touches:    new tests/test_s022_secrets.py; MANUAL.md known issues
excludes:   redaction at write time, which would contradict the verbatim guarantee of AGENTS.md section 9; generic entropy or bare-hex heuristics, which false-positive on the shas this worklog is full of
decisions:  DEC-024
closes:     2026-08-06_adversarial-F08
blocks:
paused_by:
done:      2026-08-06: tests/test_s022_secrets.py fails on prefixed key shapes and PEM headers in adocs/worklog.md, non-vacuous by construction. Red observed on the real file by planting a synthetic AWS key and restoring it. Suite 155 OK, --validate green. README test count 151 to 155; MANUAL gained a known-issues entry stating prompts are verbatim, the rotate-first escape procedure, and the three limits of the check. S031 created for the gap that the check does not travel to repositories installing the plugin.
