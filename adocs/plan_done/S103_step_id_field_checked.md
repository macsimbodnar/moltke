id:         S103
goal:       a step file's id: field agrees with its filename, or does not exist
accepts:    A step file whose `id:` disagrees with its filename is reported by
            --validate with exit 1, naming both, or the field is dropped from
            templates/step_template.md and write_step so nothing carries an id
            that means nothing. One of the two, not neither.
            The reproduction closes: copying templates/step_template.md to
            adocs/plan_todo/S050_hand_written.md and listing it in plan.md no
            longer leaves --validate green over a file whose first line says S000.
            Every existing step file across the three plan directories still
            passes, which is the non-vacuity anchor: 103 files carry the field and
            all of them agree with their names today.
            A test builds the disagreeing file and asserts the chosen behaviour;
            it fails without the change.
touches:    bin/moltke.py invariant checks or write_step; templates/step_template.md;
            AGENTS.md and templates/AGENTS.md if the documented layout changes;
            tests/test_s003_invariants.py
excludes:   deriving the id from the field instead of the filename, which every
            reader does today and which is not what this changes; renumbering or
            renaming anything that exists
decisions:
closes:     2026-08-09_adversarial-F07
blocks:
paused_by:
done:      2026-08-09: INV-6 compares a step file's id: field against its filename, closing 2026-08-09_adversarial-F07 and the last finding of that run. write_step was the only place id appeared as a field key and every reader took the id from the filename, so nothing compared the two: templates/step_template.md ships id: S000, and copying it by hand, which AGENTS.md documents as the step format, produced a file whose first line contradicted its name with --validate green. Cosmetic in behaviour, since every check keys on the filename, and it mattered as a rule stated in the ruleset's step layout and enforced nowhere. Checking is the smaller of the two fixes the finding offered and makes the documented layout true; dropping the field would have moved AGENTS.md, its shipped template and write_step together. An absent field is not reported, because the id the tool acts on is the filename either way. 4 tests, red observed on one, built by copying the template exactly as the finding did; the other three are anchors, including this repository's own 106 step files. Suite 444 OK, --validate green. README test count 440 to 444; MANUAL checked, no change — it does not document the step-file layout, which lives in AGENTS.md; specs gained a dated note and the INV-6 row now states the second half.
