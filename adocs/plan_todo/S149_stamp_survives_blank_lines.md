id:         S149
goal:       a multi-line --stamp round-trips, or a blank line in one is refused
accepts:    a --stamp containing a blank line either round-trips through parse_step_file intact or is refused at write time with the condition named; whichever is chosen is what specs.md says; red observed first
touches:    bin/moltke.py with_field, parse_step_file, field_value_problem; specs.md
excludes:   changing the twelve-space continuation format for fields that already round-trip
decisions:
closes:     2026-08-19_adversarial-F09
blocks:
paused_by:
done:
