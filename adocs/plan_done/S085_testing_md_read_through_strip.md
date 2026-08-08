id:         S085
goal:       testing.md is read through strip_guidance like every other scanner input
accepts:    adocs/testing.md is read through strip_guidance like every other scanner input, so a fenced example row in the template cannot complete a step or satisfy INV-5; the file joins stripped_files and therefore INV-13's scan, or the decision not to is recorded; red observed by completing a step against a fenced example row
touches:    bin/moltke.py inv_5_done_evidence and step_done's testing row check; tests
excludes:   changing what counts as a testing row
decisions:  
closes:     2026-08-08_adversarial.3-F06
blocks:
paused_by:
done:      2026-08-08: adocs/testing.md is read through read_stripped by INV-5 and by --step done, and joins stripped_files and therefore INV-13 scan. It was the last scanner input read raw, so a row inside a code fence — guidance by the rule specs states as universal — counted as evidence and completed a step with --validate green afterwards. Adding the reader without adding the file to the guarded set failed the S072 functional guard, which is that guard working three steps after it was built; the suite went 370 with one failure, then 370 OK. 3 tests, red observed on both the completion and the invariant. Suite 370 OK, --validate green. README test count 367 to 370; MANUAL needed no change; specs gained a dated note.
