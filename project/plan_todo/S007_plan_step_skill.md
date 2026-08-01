id:         S007
goal:       plan_step skill
accepts:    every transition (create, promote to current, pause parent and promote blocking child, complete, regenerate status.md from the filesystem) leaves INV-1..INV-7 satisfied; completion is refused when the gate conditions are unmet, with the specific missing condition named
touches:    skills/plan_step/
decisions:  DEC-007, DEC-008, DEC-009
done:
