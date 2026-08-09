id:         S088
goal:       --step new and --step block refuse a name outside [A-Za-z0-9_]+
accepts:    --step new fix-parser refuses on stderr with exit 1, names the accepted
            character set, and writes nothing: no file in plan_todo/, no entry in
            plan.md, --validate still exit 0.
            --step block <parent> fix-parser does the same and leaves the parent
            unpaused.
            --step new "../../../escaped" refuses; no file appears outside the
            marked root and no stray directory is left behind.
            A test runs --step new with a hyphenated name and asserts --validate
            still exits 0; it fails without the fix.
touches:    bin/moltke.py step_new, step_block; tests/test_s0nn_step_*.py
excludes:   loosening STEP_FILE_RE to accept more characters; renaming existing
            step files; the --audit new validation at bin/moltke.py:2340, which
            already refuses and is the model to copy.
decisions:
closes:     2026-08-08_adversarial.4-F01
blocks:
paused_by:
done:      2026-08-09: --step new and --step block refuse a short name outside [A-Za-z0-9_]+ before either touches the filesystem, closing 2026-08-08_adversarial.4-F01. The name went unchecked into the filename while STEP_FILE_RE requires that set, so 'fix-parser' filed a step every scanner skips while plan.md listed the id — --validate green over the listed-but-absent half of INV-3, created by the tool meant to keep the two in step — and a separator escaped the plan directory as S004_../../../escaped.md. Checked in mode_step rather than in either function, because both write the plan entry before the step file (S083) and a refusal halfway would leave plan.md naming a step that does not exist; --audit new since S040 is the model. 7 tests, red observed on all of them. Suite 383 OK, --validate green. README test count 376 to 383; MANUAL's two --step rows now state the rule; specs gained a dated note.
