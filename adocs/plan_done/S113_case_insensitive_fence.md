id:         S113
goal:       the pre-write rules match paths the way the filesystem does
accepts:    On a case-insensitive filesystem, --pre-write refuses
            ADOCS/PLAN_DONE/notes.md (it resolves into the real plan_done/) and
            permits Adocs/plan_todo/S099_x.md as the step file it is. On a
            case-sensitive filesystem behaviour is unchanged. The rule follows
            the path's resolved identity, not its spelling. Tests cover both
            directions and fail without the fix on this Mac.
touches:    bin/moltke.py mode_pre_write path resolution; tests/test_s005_hooks.py
excludes:   the reviewer fence's agent matching; non-macOS case-insensitive
            emulation
decisions:
closes:     2026-08-11_adversarial-F02
blocks:
paused_by:
done:      2026-08-11: --pre-write follows the path's resolved identity instead of its spelling, closing 2026-08-11_adversarial-F02. The rules compared rel.parts against lowercase literals and resolve() does not fold case, so on the case-insensitive filesystem this project ships on, ADOCS/PLAN_DONE/notes.md wrote into the real plan_done/ at exit 0 while a legitimate step file spelled Adocs/ was refused with a message untrue on this filesystem. _canonical_case renames each existing component to the directory entry it actually is via samefile, keeps a missing component as typed, and swallows unreadable directories; on a case-sensitive filesystem a variant path does not exist, nothing folds, behaviour unchanged. 3 tests, red observed on both directions, skipping with a message where the filesystem cannot express the case. Suite 449 OK, --validate green. README test count 446 to 449; MANUAL checked, no change — the fence's documented behaviour is what it now actually does.
