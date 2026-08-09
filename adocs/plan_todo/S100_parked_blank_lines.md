id:         S100
goal:       the Parked block is carried through as verbatim as the docs say
accepts:    A Parked block containing blank lines between entries, and a section
            below it, survives --step status unchanged: the blank lines are still
            there and the section is still separated from the list.
            Repeated regeneration does not grow the file: trailing blank lines are
            trimmed, and a second and third --step status produce byte-identical
            output.
            specs.md and skills/step/SKILL.md already say "verbatim"; after this
            they are true rather than amended, or the sentence is narrowed to what
            the code does. One of the two, not neither.
            A test writes a Parked block with blank lines and a heading below it
            and asserts both survive; it fails without the fix.
touches:    bin/moltke.py parked_lines; tests/test_s007_step.py; adocs/specs.md
            and skills/step/SKILL.md only if the promise is narrowed instead
excludes:   any other part of status.md, all of which is derived and regenerated;
            reopening where the Parked block starts, which S094 settled
decisions:
closes:     2026-08-09_adversarial-F04
blocks:
paused_by:
done:
