id:         S055
goal:       INV-13 counts the markers strip_guidance actually sees
accepts:    a fence marker inside an HTML comment does not make INV-13 report a file, because strip_guidance removes comments before pairing and so never sees it; INV-13 and strip_guidance agree on what a marker is; a genuinely unclosed fence outside a comment is still reported; red observed with a commented marker blocking --stop under a message that is false for that file
touches:    bin/moltke.py inv_13_balanced_fences; tests/test_s033_fences.py
excludes:   changing what strip_guidance strips
decisions:
closes:     2026-08-07_adversarial.2-F08
blocks:
paused_by:
done:      2026-08-08: INV-13 and strip_guidance share one fence_markers, which removes HTML comments and then finds line-anchored markers, so the invariant counts exactly what the stripper pairs. A marker inside a comment was counted by the check and not by the thing it protects, blocking --stop under a message false for that file; the same divergence hid a real imbalance when a commented marker made the raw count even. Both directions gone. 3 tests, red observed in both directions, plus the finding's transcript re-measured: exit 0 and exit 0 where it measured 1 and 2. Suite 261 OK, --validate green. README test count 258 to 261; MANUAL's fence entry now says a commented marker is not a marker; specs gained a dated note.
