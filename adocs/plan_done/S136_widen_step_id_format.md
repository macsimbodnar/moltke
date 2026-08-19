id:         S136
goal:       step ids past 999 are recognised everywhere, or allocation is refused loudly
accepts:    a step file whose id has four digits is seen by the plan reader, every invariant, the `--pre-write` step-file fence, the derived next step, and the plan-entry scan — observed red first against today's three-digit pattern; allocation past the widest recognised form refuses with the condition named rather than minting an id nothing will read again; the id counter never returns an id that already exists
touches:    bin/moltke.py STEP_FILE_RE and every `S\d{3}` scan, tests/test_s003_invariants.py, tests/test_s007_step.py
excludes:   renumbering any existing id (DEC-008)
decisions:  DEC-055
closes:     2026-08-18_adversarial-F06
blocks:
paused_by:
done:      2026-08-19: the recognised step id is three digits or four, stated once as STEP_ID_DIGITS and reused by STEP_ID_RE, STEP_FILE_RE and PLAN_ENTRY_RE, closing 2026-08-18_adversarial-F06. Five scans each spelled the pattern themselves, so past S999 there was not one blind spot but five, and unanchored the field scans were worse than blind: paused_by S1000 matched S100, reported as a phantom pause on a step nobody wrote, and a blocks: S1000 target was invisible to INV-4 for the same reason. The id counter is now deliberately wider than the readers — any id-shaped filename at any width, any three-or-more-digit token in plan.md — so a width nothing else reads bumps the counter instead of being handed out twice, and lands as S097's refusal, which moves to S9999 (DEC-055). 11 tests added, red observed on 12 before the fix: 7 of 9 readers tests, 5 of 8 ceiling tests, the rest non-vacuity anchors. Suite 452 OK (3 skip on a case-sensitive filesystem), --validate green. specs.md's --step new row states the widened form and the new ceiling; README's test count was already stale at 427 and is now 452 with the skips named; MANUAL checked, no change — it documents no id ceiling, and its --step new row is about the name half of the filename.
author:    Maksym Bodnar
