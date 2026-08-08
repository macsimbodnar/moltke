id:         S075
goal:       INV-14 names the cause it can prove and a remedy that works
accepts:    INV-14 names the cause it can prove: a finding heading hidden inside an HTML comment is reported as swallowed by a code fence, and the remedy it prints cannot be followed; the message distinguishes the two, or stops claiming which one it is; red observed with the commented heading and the unfollowable remedy
touches:    bin/moltke.py inv_14_findings_not_hidden and hidden_findings; tests/test_s033_fences.py
excludes:   changing what strip_guidance removes
decisions:  
closes:     2026-08-08_adversarial.2-F09
blocks:
paused_by:
done:      2026-08-08: INV-14 strips comments before comparing, so what it reports is always something a fence can hide. strip_guidance removes HTML comments as well as fences, so a draft finding commented out — which the shipped template invites, its own append marker being a comment — was reported as swallowed by a code fence in a report with no fence markers at all, with a remedy that could not be applied, repeated to --stop and --post-write as a blocking problem. Commented content is guidance everywhere else in the tool, and this makes INV-14 agree with that. 2 tests, red observed with the commented draft, and the J2 fence case asserted unchanged. Suite 342 OK, --validate green. README test count 340 to 342; MANUAL needed no change, since it describes what a fence hides; specs gained a dated note and INV-14 line gained a clause.
