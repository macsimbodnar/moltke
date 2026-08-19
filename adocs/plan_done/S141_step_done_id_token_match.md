id:         S141
goal:       `--step done` reads paused_by and blocks as tokens, never as substrings
accepts:    `--step done` clears a pause only when `paused_by` names that exact id as a token, and refuses on `blocks:` only when that field names it as a token; red observed first on all three directions with the reviewer's TestStepDoneMatchesIdsAsTokens; the dated-comment collision (paused_by S201 with S010 in the comment) and the S100/S1000 collision both stop reproducing; --validate stays green across a completion that touches neither
touches:    bin/moltke.py step_done, the three `step_id in field_value(...)` comparisons at :2365, :2387, :2411; tests/test_2026_08_19_adversarial_findings.py
excludes:   changing what `--step block` writes into paused_by, and the dated-comment format itself
decisions:
closes:     2026-08-19_adversarial-F01
blocks:
paused_by:
done:      2026-08-19: closes 2026-08-19_adversarial-F01. The three comparisons in step_done that asked whether an id occurred anywhere in a field's text now read tokens: blocks_ids() for the blocks: site, pauser_id() == step_id for both paused_by sites. blocks_ids is stated once beside pauser_id and INV-4's reader was routed through it, so the rule lives in one place the way STEP_ID_DIGITS does since DEC-055. Red observed first on all three directions of the reviewer's TestStepDoneMatchesIdsAsTokens: 'S200 unpaused' printed while completing an unrelated S010 named only in the pause's dated comment, S200's pause on the open S1000 cleared by completing S100, and a completion refused by a blocks: field naming S1000 while quoting S100. All three green now. Per DEC-058 this commit also carries F03's fix, because one reviewer-written test file gates both findings and the completion gate reads the whole suite, so no ordering completes this step before F03 is fixed too. Suite 457 OK (3 skip), --validate green. specs.md unchanged for this finding: its INV-1 wording already described the behaviour the code now has; the wording that did move belongs to F03 and is described in S143. README and MANUAL checked, no change owed by this finding.
author:    Maksym Bodnar
