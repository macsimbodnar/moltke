id:         S091
goal:       --scaffold and --decline refuse instead of tracebacking, and leave no half-applied marker
accepts:    In an unwritable directory both --scaffold and --decline print a refusal
            naming the path and exit 1 with no Python traceback on stderr, matching
            MANUAL.md:178.
            With adocs present as a regular file, --scaffold refuses and the
            directory is left without an enabled .moltke.json, so no hook is live
            against a tree that was never built.
            Two tests, one per mode, assert stderr carries no "Traceback"; both fail
            without the fix.
touches:    bin/moltke.py mode_scaffold, mode_decline, main's dispatch order;
            tests/test_s0nn_scaffold*.py
excludes:   main's existing backstop, which runs after the marker gate and cannot
            cover these two modes; changing SCAFFOLD_MAP's contents.
decisions:
closes:     2026-08-08_adversarial.4-F04
blocks:
paused_by:
done:
