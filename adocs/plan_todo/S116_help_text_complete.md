id:         S116
goal:       --help names every operation the parser accepts
accepts:    --help output names unpause among the --step operations and check
            among the --audit operations. A test renders build_parser()'s help
            and asserts every STEP_OPS and AUDIT_OPS member appears; it fails
            today on unpause and check.
touches:    bin/moltke.py build_parser help strings; tests/test_s009_surface.py
excludes:   restructuring the parser; the golden format
decisions:
closes:     2026-08-11_adversarial-F05
blocks:
paused_by:
done:
