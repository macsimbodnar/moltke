id:         S049
goal:       two unclosed fences cannot hide a finding
accepts:    the J2 case from 2026-08-07_adversarial-F02 no longer hides the finding between two unclosed fences, which is an even marker count and so invisible to INV-13; whatever rule is chosen states in specs the case it cannot see, since S033 measured that no content heuristic separates two unclosed fences from one closed fence and the templates deliberately put headings inside fences; red observed by re-running that case verbatim, where --validate exits 0 and --audit list omits the finding entirely
touches:    bin/moltke.py strip_guidance and inv_13_balanced_fences; tests/test_s033_fences.py; adocs/specs.md; MANUAL.md
excludes:   a full markdown parser; reverting S033, which fixed the odd-count and recap-gate halves
decisions:
closes:     2026-08-07_adversarial-F02
blocks:
paused_by:
done:
