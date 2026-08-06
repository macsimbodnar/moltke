id:         S021
goal:       optional test_command gate on --step done
accepts:    with test_command set, --step done runs it and refuses on a non-zero exit, naming the failure and showing the output tail; with it absent, behaviour is exactly as today and the refusal path says the gate is not configured; a non-string test_command is a marker violation; schema stays 1 so no existing marker needs migration
touches:    bin/moltke.py check_marker and step_done; templates/moltke.json; MANUAL.md; AGENTS.md and templates/AGENTS.md; adocs/specs.md; tests/test_s007_step.py
excludes:   making test_command required; a schema bump; running the suite from any mode other than --step done
decisions:  DEC-023
closes:     2026-08-06_adversarial-F07
blocks:
paused_by:
done:      2026-08-06: optional test_command in .moltke.json; --step done runs it from the repo root under a 600s timeout and refuses with the last 20 lines on failure; absent, it says out loud that nothing ran the suite. Non-string or blank is a marker violation. Schema stays 1. 6 tests, red observed. Suite 151 OK, --validate green. README test count 145 to 151; MANUAL gained the key in the marker block plus a paragraph on it and narrowed the mechanical-gate entry; AGENTS.md and templates/AGENTS.md changed identically; init skill now asks for the test command.
