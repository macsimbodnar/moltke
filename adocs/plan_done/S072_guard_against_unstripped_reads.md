id:         S072
goal:       the structural guard against an unguarded scanner can fire again
accepts:    the S063 structural guard fires again: it looked for strip_guidance beside read_text, and S064 banned read_text everywhere, so a new scanner written the mandated way reads an unguarded file with the suite green; whatever replaces it is checked by adding such a consumer and watching the suite go red; red observed by doing exactly that
touches:    tests/test_s033_fences.py; bin/moltke.py if the guard needs a hook to check against
excludes:   reverting either S063 or S064
decisions:  
closes:     2026-08-08_adversarial.2-F06
blocks:
paused_by:
done:      2026-08-08: the structural guard names the three lines allowed to call strip_guidance, instead of looking for it beside read_text. S064 banned read_text everywhere, so the mandated way to write a new scanner — strip_guidance(read_file(path)) — passed the old guard: it was vacuous by construction, which is the shape it existed to catch, applied to itself. A second test runs --validate and the session context with read_stripped recorded and asserts every file it was pointed at is one INV-13 guards, which no rewrite of the source can dodge. Red observed by planting the finding's own testing_rows scanner verbatim in a copy outside the repository, where the old guard left all 308 green. Suite 338 OK, --validate green. README test count 337 to 338; MANUAL needed no change; the specs sentence describing the old guard is amended in place.
