id:         S005
goal:       hooks wiring, all five events, verified against live docs
accepts:    hooks/hooks.json wires SessionStart, UserPromptSubmit, PreToolUse (Write and Edit), PostToolUse, Stop to the moltke.py modes per specs; event names and JSON schema verified against current Claude Code documentation, not the shapes in specs; every blocking message states exactly what to do to unblock (INV-12); every hook exits 0 without the marker
touches:    hooks/hooks.json, bin/moltke.py
decisions:  DEC-005, DEC-006
done:       2026-08-01 suite green 49/49; hook contract verified against live docs (UserPromptSubmit erase-on-2, SessionStart additionalContext, no Stop cap -> self-imposed); red observed (8 failures, 2 errors); testing.md rows added; README and MANUAL checked, absent by plan (S011)
