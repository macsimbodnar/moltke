id:         S055
goal:       INV-13 counts the markers strip_guidance actually sees
accepts:    a fence marker inside an HTML comment does not make INV-13 report a file, because strip_guidance removes comments before pairing and so never sees it; INV-13 and strip_guidance agree on what a marker is; a genuinely unclosed fence outside a comment is still reported; red observed with a commented marker blocking --stop under a message that is false for that file
touches:    bin/moltke.py inv_13_balanced_fences; tests/test_s033_fences.py
excludes:   changing what strip_guidance strips
decisions:
closes:     2026-08-07_adversarial.2-F08
blocks:
paused_by:
done:
