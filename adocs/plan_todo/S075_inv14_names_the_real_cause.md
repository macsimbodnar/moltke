id:         S075
goal:       INV-14 names the cause it can prove and a remedy that works
accepts:    INV-14 names the cause it can prove: a finding heading hidden inside an HTML comment is reported as swallowed by a code fence, and the remedy it prints cannot be followed; the message distinguishes the two, or stops claiming which one it is; red observed with the commented heading and the unfollowable remedy
touches:    bin/moltke.py inv_14_findings_not_hidden and hidden_findings; tests/test_s033_fences.py
excludes:   changing what strip_guidance removes
decisions:  
closes:     2026-08-08_adversarial.2-F09
blocks:
paused_by:
done:
