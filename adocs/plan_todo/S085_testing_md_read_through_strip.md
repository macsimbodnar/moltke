id:         S085
goal:       testing.md is read through strip_guidance like every other scanner input
accepts:    adocs/testing.md is read through strip_guidance like every other scanner input, so a fenced example row in the template cannot complete a step or satisfy INV-5; the file joins stripped_files and therefore INV-13's scan, or the decision not to is recorded; red observed by completing a step against a fenced example row
touches:    bin/moltke.py inv_5_done_evidence and step_done's testing row check; tests
excludes:   changing what counts as a testing row
decisions:  
closes:     2026-08-08_adversarial.3-F06
blocks:
paused_by:
done:
