id:         S007
goal:       step skill
accepts:    every transition (create, promote to current, pause parent and promote blocking child, complete, regenerate status.md from the filesystem) leaves INV-1..INV-7 satisfied; completion is refused when the gate conditions are unmet, with the specific missing condition named
touches:    skills/step/
decisions:  DEC-007, DEC-008, DEC-009
done:      2026-08-01 suite green 82/82; red observed before each behaviour; end-to-end lifecycle verified on a throwaway repo; README and MANUAL checked, absent by plan (S011)
