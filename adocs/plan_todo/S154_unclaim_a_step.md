id:         S154
goal:       the lifecycle can undo a claim, returning a step to plan_todo/ without a by-hand move
accepts:    a claimed step returns to plan_todo/ through the tool, refusing when the step has children in plan_current/ or a done stamp, and clearing nothing else; the author field is dropped or kept by a stated rule; the surface golden, specs table and MANUAL all name the new operation; red observed first
touches:    bin/moltke.py --step operations, tests/surface.py, the golden, specs.md, MANUAL.md
excludes:   resuming a step out of plan_done/, which DEC-008 and INV-7 forbid
decisions:  DEC-058
closes:
blocks:
paused_by:
done:
