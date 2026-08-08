id:         S051
goal:       MANUAL stops claiming the two-unclosed-fence hole is fixed
accepts:    MANUAL's fence entry describes what reproduces at HEAD rather than putting it in the past tense; it is corrected whether or not S049 has landed, and reads correctly either way; no other live document claims the hole is closed
touches:    MANUAL.md; adocs/specs.md
excludes:   fixing the hole itself, which is S049
decisions:
closes:     2026-08-07_adversarial.2-F04
blocks:
paused_by:
done:      2026-08-08: doc-only. MANUAL's fence entry was already corrected in S049's commit — it now states what INV-13 covers, what INV-14 covers, and what neither does, instead of the past-tense claim that the hole closed before 0.4.0. This step adds the missing half: the specs S033 note said the two-unclosed-fence case is reported rather than guessed, true of an odd count only, and now carries a dated amendment pointing at INV-14. Live documents grepped for further claims; none. No code change, so no new tests: the behaviour these claims describe is pinned by the S049 tests. Suite 258 OK, --validate green. README needed no change; MANUAL and specs are the two files this step is about.
