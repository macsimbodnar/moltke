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
done:
