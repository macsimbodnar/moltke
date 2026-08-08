id:         S094
goal:       --step status carries an unindented Parked list through, or refuses
accepts:    A status.md whose Parked entries are written flush left survives
            --step status: every entry is still there afterwards.
            If the chosen remedy is a refusal instead, it exits 1, names the shape
            it could not read, and writes nothing.
            The shipped template shows an accepted Parked entry, so the shape is
            visible rather than inferred.
            A test writes an unindented parked entry and asserts it survives
            --step status; it fails without the fix.
touches:    bin/moltke.py parked_lines; templates/ status template;
            tests/test_s0nn_status*.py; skills/step/SKILL.md and MANUAL.md if the
            documented promise changes.
excludes:   any other part of status.md, all of which is derived and regenerated.
decisions:
closes:     2026-08-08_adversarial.4-F07
blocks:
paused_by:
done:
