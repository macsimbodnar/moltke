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
done:
