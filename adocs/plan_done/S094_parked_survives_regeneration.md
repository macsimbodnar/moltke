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
done:      2026-08-09: --step status carries everything below - Parked: to the end of the file through a regeneration, verbatim and whatever its indentation, closing 2026-08-08_adversarial.4-F07. The collector kept only lines starting with two spaces or a tab and stopped at the first that did not, so a Parked list written flush left — ordinary markdown, and what the shipped template's bare heading invited — was deleted by a command that runs at every step transition and reports success. Reading to the end of the file is safe because Parked is the last block step_status writes, so nothing derived follows it, and keeping lines verbatim means the shape written is the shape read back, which a three-regeneration test pins. The template now carries a Parked entry, so the block is visible rather than inferred. 5 tests, red observed on four; the fifth is S007's indented-list test, kept as the anchor for the old shape. Suite 403 OK, --validate green. README test count 399 to 403; MANUAL's hook list and skills/step/SKILL.md both state what is carried and that indentation does not matter; specs gained a dated note.
