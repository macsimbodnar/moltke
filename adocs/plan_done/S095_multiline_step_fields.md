id:         S095
goal:       a continuation line in a step field is read, or the field is refused
accepts:    parse_step_file at bin/moltke.py:86 keeps a field's indented
            continuation lines instead of dropping them: a done: stamp whose
            README and MANUAL check sits on its second line satisfies the Stop
            stamp gate at bin/moltke.py:1432 and --step done at bin/moltke.py:1888,
            and a test asserts exactly that and fails without the fix.
            Whatever is chosen, the silent half is gone: either the continuation
            is read, or a field with dropped continuation lines is reported as a
            problem naming the file and the field. Truncating and saying nothing
            is what this step removes.
            The other fields parsed from the same function keep working —
            goal:, accepts:, touches:, excludes: already span lines across
            plan_todo/ and plan_done/, so a fix that changes how they read must
            leave --validate exit 0 over this repository, which is the
            non-vacuity anchor.
            A field line whose continuation begins with something that looks like
            another field (`note: x`) still starts a new field, not a
            continuation, and a test pins that boundary.
touches:    bin/moltke.py parse_step_file and any caller that reads a
            multi-line field; tests/test_s0nn_step_*.py
excludes:   rewriting existing step files to fit whatever is chosen; changing the
            single-line stamp convention every plan_done/ file already follows;
            the Stop gate's wording, which was correct about what it saw
decisions:
closes:
blocks:
paused_by:
done:      2026-08-09: a step field folds its indented continuation lines into its value. parse_step_file matched per line and a continuation matches nothing, so every field was silently truncated to its first line — found live during S059, where the Stop stamp gate reported the README and MANUAL check missing from a stamp that recorded it two lines down, and the gate was right about what it could see. goal:, accepts:, touches: and excludes: span lines throughout the plan directories, so every reader of those had been seeing the opening line alone. A flush-left word: starts a new field, a blank line ends one, and only an indented non-empty line continues it. with_field now drops the lines a replaced value spanned, because leaving them would fold the old text straight back in: the same silent defect in a new place. 7 tests, red observed on three. One asserts an absence, so it has a twin that changes only the words on the second line and still fails — the first version of it had an unfalsifiable precondition and was rewritten. Suite 410 OK, --validate green. README test count 403 to 410; MANUAL checked, no change — it documents no step-file field syntax; specs gained a dated note.
