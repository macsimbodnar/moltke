id:         S078
goal:       INV-16 compares the two sides instead of testing both for emptiness
accepts:    INV-16 compares the raw prime-directive section against the stripped one rather than testing both for emptiness, so a directive fenced beside other prose is reported instead of passing; the specs sentence describing it as a comparison becomes true; red observed with the mixed section
touches:    bin/moltke.py inv_16_prime_directive_readable; tests/test_s033_fences.py; adocs/specs.md
excludes:   changing what counts as a written directive for the planning nudge
decisions:  
closes:     2026-08-08_adversarial.2-F12
blocks:
paused_by:
done:
