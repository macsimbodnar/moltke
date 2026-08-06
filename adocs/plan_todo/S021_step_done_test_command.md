id:         S021
goal:       optional test_command gate on --step done
accepts:    with test_command set, --step done runs it and refuses on a non-zero exit, naming the failure and showing the output tail; with it absent, behaviour is exactly as today and the refusal path says the gate is not configured; a non-string test_command is a marker violation; schema stays 1 so no existing marker needs migration
touches:    bin/moltke.py check_marker and step_done; templates/moltke.json; MANUAL.md; AGENTS.md and templates/AGENTS.md; adocs/specs.md; tests/test_s007_step.py
excludes:   making test_command required; a schema bump; running the suite from any mode other than --step done
decisions:  DEC-023
closes:     2026-08-06_adversarial-F07
blocks:
paused_by:
done:
