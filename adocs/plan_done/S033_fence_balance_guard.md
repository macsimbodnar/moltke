id:         S033
goal:       an unbalanced code fence cannot hide content from a scanner
accepts:    strip_guidance no longer deletes to end-of-file on an odd number of ``` markers; a report with an unclosed fence still exposes its findings to INV-10 and --audit list, and a worklog with one still exposes its recap headings to the Stop gate; the suite fails loudly on an unbalanced fence in a scanned file rather than silently dropping content; red observed with the audit report that reproduced this on itself, where --audit list saw 2 of 11 findings
touches:    bin/moltke.py strip_guidance; tests/test_s004_invariants.py; tests/test_s008_audit.py; tests/test_s005_hooks.py
excludes:   a full markdown parser; nested or tilde fences beyond what the repository actually writes
decisions:
closes:     2026-08-07_adversarial-F02
blocks:
paused_by:
done:      2026-08-07: strip_guidance pairs line-anchored fence markers in order and leaves a trailing unpaired marker as text; new INV-13 reports an odd marker count in plan.md, decisions.md, worklog.md, and every audit report, because two unclosed fences are indistinguishable from one closed fence and the templates put headings inside fences on purpose. 13 tests, red observed, plus both of the finding's live reproductions re-run. Suite 200 OK, --validate green. README test count 187 to 200; MANUAL gained a known-issues entry on unclosed fences; specs gained INV-13 and a dated note. Deviation from touches: an invariant rather than a suite-only check, so the guarantee travels to installed repositories instead of protecting moltke alone.
