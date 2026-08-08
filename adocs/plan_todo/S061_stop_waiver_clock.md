id:         S061
goal:       the Stop waiver clock does not freeze when prompt logging fails
accepts:    a --log-prompt failure, which S014 already detects and records a breadcrumb for, no longer freezes stop_turn_key's turn counter into the .2-F01 off switch: eight distinct turns with a failing append and a standing violation each block rather than reading 2 2 2 0 0 0 0 0; whatever replaces or corroborates the worklog heading count is stated in specs alongside what it still cannot distinguish; the DEC-029 property S047 restored is re-measured and unchanged for the ordinary path, where eight real turns read 2 2 2 2 2 2 2 2 and eight retries inside one turn read 2 2 2 0 0 0 0 0; red observed with the failing-append fixture
touches:    bin/moltke.py stop_turn_key and the log-failure breadcrumb; tests/test_s005_hooks.py; adocs/specs.md
excludes:   making --log-prompt blocking, which would erase the user's prompt; reverting S047
decisions:  DEC-029
closes:     2026-08-08_adversarial-F02
blocks:
paused_by:
done:
