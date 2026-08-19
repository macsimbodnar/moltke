id:         S142
goal:       the golden guards hook matchers and mode flags, not just event names
accepts:    dropping the Write|Edit PreToolUse matcher, or repointing the Stop hook at another mode, fails the suite; tests/surface.py declares (event, matcher, mode flag) triples and the golden carries them; red observed first by mutating hooks.json in a scratch copy while the suite was still green
touches:    tests/surface.py, tests/test_s009_surface.py, the refreshed golden
excludes:   changing hooks/hooks.json itself, and guarding hook argument order beyond the mode flag
decisions:
closes:     2026-08-19_adversarial-F02
blocks:
paused_by:
done:      The golden read only the set of hook event names, so a mutated tree with the Write|Edit PreToolUse matcher deleted and Stop pointed at --roadmap ran 457 tests OK. tests/surface.py now declares (event, matcher, mode flag) triples and the golden carries one line per hook command; TestHookWiringIsGuarded adds the part a refresh cannot silence — every hook-only mode is wired, every wired mode is a real parser flag, both write modes select Write and Edit, and Stop invokes --stop. HOOK_MODES is hand-maintained: nothing in the parser says which modes exist only for a hook, and deriving mode lists is S150's subject. README stopped claiming the golden covers only event names; specs states the wiring is guarded. MANUAL checked, unchanged: the wiring is not a user-operable surface.
author:    Maksym Bodnar
