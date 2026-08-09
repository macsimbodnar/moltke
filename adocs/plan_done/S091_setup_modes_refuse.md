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
done:      2026-08-09: --scaffold and --decline guard their own writes and refuse with exit 1 instead of raising, closing 2026-08-08_adversarial.4-F04. Both are dispatched before main's backstop and have to be, since that backstop runs after the marker gate they exist to create, so an unwritable directory reached the user as a Python traceback — which MANUAL has claimed no mode produces since 0.6.0. --scaffold also rolls back what the failing run created: the marker is the first entry in SCAFFOLD_MAP, so a failure partway through left an enabled .moltke.json over a tree that was never built, every hook live against nothing. Only files that run created are removed, scaffolding never overwrites, and anything that could not be removed is named in the refusal. 4 tests, red observed on three, all three with a full traceback on stderr; the fourth is the non-vacuity anchor, and the permission tests skip with a message under root rather than passing silently. Suite 396 OK, --validate green. README test count 392 to 396; MANUAL's no-traceback paragraph now states where these two modes sit relative to that catch; specs gained a dated note.
