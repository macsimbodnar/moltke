id:         S078
goal:       INV-16 compares the two sides instead of testing both for emptiness
accepts:    INV-16 compares the raw prime-directive section against the stripped one rather than testing both for emptiness, so a directive fenced beside other prose is reported instead of passing; the specs sentence describing it as a comparison becomes true; red observed with the mixed section
touches:    bin/moltke.py inv_16_prime_directive_readable; tests/test_s033_fences.py; adocs/specs.md
excludes:   changing what counts as a written directive for the planning nudge
decisions:  
closes:     2026-08-08_adversarial.2-F12
blocks:
paused_by:
done:      2026-08-08: INV-16 compares the prime-directive section against its stripped form, which is what specs already claimed it did. It returned clean as soon as prime_directive was non-empty, so a section holding a lead-in sentence and the rule itself inside a fence passed: the directive unreadable, nothing reporting it, and prime_directive answering with the lead-in. The section is one sentence by design, so anything a fence removes from it is content no check can read. hides_content holds the comparison INV-14 and INV-16 both make, which also keeps it inside the short list of lines allowed to call strip_guidance — the S072 guard caught the first attempt, which is that guard working four steps after it was built. 4 tests, red observed. Suite 351 OK, --validate green. README test count 347 to 351; MANUAL needed no change; specs gained a dated note and the INV-16 line a clause.
