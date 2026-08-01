id:         S005
goal:       hooks wiring, all five events, verified against live docs
accepts:    hooks/hooks.json wires SessionStart, UserPromptSubmit, PreToolUse (Write and Edit), PostToolUse, Stop to the workflow_check.py modes per specs; event names and JSON schema verified against current Claude Code documentation, not the shapes in specs; every blocking message states exactly what to do to unblock (INV-12); every hook exits 0 without the marker
touches:    hooks/hooks.json, bin/workflow_check.py
decisions:  DEC-005, DEC-006
done:
