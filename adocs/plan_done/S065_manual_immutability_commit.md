id:         S065
goal:       MANUAL says which commit an immutability violation names
accepts:    MANUAL.md:308 stops saying the violation "names the commit that did it" and says what the message actually carries, traced to the code that produces it; the sentence reads correctly for both the uncommitted and the committed case; this is the residual of .2-F07 that S054 corrected around
touches:    MANUAL.md; adocs/specs.md if it repeats the claim
excludes:   changing what the violation message says, which is a behaviour change and not this step
decisions:
closes:     2026-08-08_adversarial-F06
blocks:
paused_by:
done:      2026-08-08: MANUAL's immutability paragraph said the violation names the commit that did the tampering. It names the commit it compares against — the one that added the plan_done/ file, or the high-water mark for decisions.md — and the tampering commit appears nowhere, so a reader ran git show on the legitimate commit that first added the file. Corrected to say which commit is named and that restoring those bytes in a new commit is what clears it, matching the paragraph five lines below that already described the mechanism. The sentence had survived being named in two consecutive audits, so it gets a test in both directions: the message names the baseline and not the tampering sha, and MANUAL does not carry the old claim. 2 tests, red observed against the committed MANUAL, plus the transcript re-measured. Suite 308 OK, --validate green. README test count 306 to 308; specs needed no change, since it never made the claim.
