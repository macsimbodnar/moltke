id:         S030
goal:       INV-8 covers decisions.md only; the worklog is convention, not enforcement
accepts:    APPEND_ONLY_FILES holds decisions.md alone, so trimming or rewriting adocs/worklog.md is no longer a violation while rewriting or deleting decisions.md still is; INV-8's wording in specs.md is narrowed with a dated inline note and the old two-file sentence marked superseded, not deleted; AGENTS.md sections 2, 9 and 11 stop calling the worklog append-only and say it is convention, with templates/AGENTS.md changed identically so the byte-identity test stays green; the S004 INV-8 tests are re-targeted rather than deleted, the worklog case now asserting the check abstains on a trimmed worklog and the decisions.md cases unchanged; the abstain assertion first establishes that the same tampering against decisions.md does violate, so it cannot pass because the checker is broken; MANUAL and README checked for any claim that the worklog cannot be edited
touches:    bin/moltke.py APPEND_ONLY_FILES and inv_8_append_only message wording; adocs/specs.md INV-8; AGENTS.md; templates/AGENTS.md; tests/test_s004_invariants.py TestAppendOnly; MANUAL.md
excludes:   INV-7 and plan_done, which stay enforced; the committed-baseline defect, which is S018; worklog rotation or size limits; the secret-shape check, which is S022 and still wanted because detection beats redaction (DEC-024)
decisions:  DEC-025
closes:
blocks:
paused_by:
done:      2026-08-06: APPEND_ONLY_FILES is decisions.md alone; INV-8 refusal now explains the DEC id citation reason. AGENTS.md sections 2, 9, 11 and templates/AGENTS.md changed identically and id-free. S004 worklog test re-targeted, not deleted. Suite 132 OK, --validate green. README checked, no change needed: it never claimed the worklog was immutable. MANUAL updated in two places, the daily-use line and INV-8's git-baseline entry.
