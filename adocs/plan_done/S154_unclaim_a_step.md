id:         S154
goal:       the lifecycle can undo a claim, returning a step to plan_todo/ without a by-hand move
accepts:    a claimed step returns to plan_todo/ through the tool, refusing when the step has children in plan_current/ or a done stamp, and clearing nothing else; the author field is dropped or kept by a stated rule; the surface golden, specs table and MANUAL all name the new operation; red observed first
touches:    bin/moltke.py --step operations, tests/surface.py, the golden, specs.md, MANUAL.md
excludes:   resuming a step out of plan_done/, which DEC-008 and INV-7 forbid
decisions:  DEC-058
closes:
blocks:
paused_by:
done:      2026-08-20: --step unclaim moves a claimed step from plan_current/ back to plan_todo/ and clears author:, the field --step start writes and the one that means claimed; every other field is left alone. Refuses a step that is unclaimed, in plan_done/, carrying a done: stamp, renaming onto a twin id, paused (routed to whichever of --step unpause or --step done clears that pause), or declared in another plan_current step's blocks:. A blocking child is permitted and the parent it leaves paused is named with the command that resumes it, because refusing both sides of a block relation would make a claimed stack impossible to put down. Red observed first: 11 tests, all failing on unknown --step operation 'unclaim'; two were weak and were strengthened before the fix, one passing vacuously off the unknown-operation message and one failing its own precondition. Surface: golden refreshed, --help widened, rows added to the specs and MANUAL tables. Suite green, 523 tests. README and MANUAL checked, both changed; AGENTS.md and templates/AGENTS.md paragraph 4 and the step skill say the way back exists.
author:    Maksym Bodnar
