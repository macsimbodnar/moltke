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
done:
