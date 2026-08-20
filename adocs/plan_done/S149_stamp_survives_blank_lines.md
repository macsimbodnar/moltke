id:         S149
goal:       a multi-line --stamp round-trips, or a blank line in one is refused
accepts:    a --stamp containing a blank line either round-trips through parse_step_file intact or is refused at write time with the condition named; whichever is chosen is what specs.md says; red observed first
touches:    bin/moltke.py with_field, parse_step_file, field_value_problem; specs.md
excludes:   changing the twelve-space continuation format for fields that already round-trip
decisions:  DEC-059
closes:     2026-08-19_adversarial-F09
blocks:
paused_by:
done:      Refused rather than round-tripped (DEC-059): --step done rejects a --stamp containing a blank line, naming the condition, before the suite gate and before anything moves.
            Red observed first on the report's own reproduction, on a whitespace-only line, and on two leading newlines: all three exited 0 with the stamp whole on disk and parse_step_file returning the first paragraph alone.
            The fourth test is the non-vacuity anchor — a multi-line stamp with no blank line still completes and still round-trips through the same parser.
            specs.md's --step done row and MANUAL both say the condition now; MANUAL's second statement of the line-break rule claimed --stamp was refused on any line break, contradicting its own table two rows above it.
            README checked, no stamp claim in it. Suite green, 488 tests.
author:    Maksym Bodnar
