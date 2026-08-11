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
done:
