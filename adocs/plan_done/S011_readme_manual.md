id:         S011
goal:       README and MANUAL
accepts:    README covers layout, build, test, and the exact commands with every environment variable and its real semantics, and points at MANUAL for usage; MANUAL covers install, operation, known bugs; minimal overlap; every doc claim traced to the code path that produces it
touches:    README.md, MANUAL.md
note:       MANUAL known-bugs section must record DEC-020: the repository root is also the plugin root, so this repository's own project/, tests/, AGENTS.md, and CLAUDE.md are copied into every install, and `claude plugin validate --strict` warns that the root CLAUDE.md is not loaded as project context
note:       creating MANUAL.md activates the dormant surface check in test_s009_surface.py (TestSurfaceIsDocumented.test_manual_describes_every_mode_once_it_exists); confirm it stops skipping and actually passes, and that removing a mode from MANUAL makes it fail
done:      2026-08-02 suite green 110/110, no skips; MANUAL half of the surface guard verified to bite; README and MANUAL are this step's deliverable and were written against the code
