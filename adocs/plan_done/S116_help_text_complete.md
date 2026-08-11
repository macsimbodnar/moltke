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
done:      2026-08-11: --help names every operation the parser accepts, closing 2026-08-11_adversarial-F05. The golden reads argparse actions so help strings drifted silently: unpause and check were accepted and undocumented at the terminal. The two help strings now list them, and a test renders format_help() and asserts every STEP_OPS and AUDIT_OPS member appears, so the next added operation cannot drift. 1 test, red observed. Suite 453 OK, --validate green. README test count 452 to 453; MANUAL checked, no change — its mode table already documents both.
