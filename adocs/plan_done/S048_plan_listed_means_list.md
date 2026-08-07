id:         S048
goal:       INV-3 and plan_order agree on what listed in plan.md means
accepts:    a step file whose id appears in plan.md only in prose is an INV-3 violation, so it cannot pass validation while being invisible to derived_next; the reverse direction keeps reporting a list entry with no step file; INV-3's message stops claiming a phantom is the derived next step, which S045 made false; red observed with the finding's fixture, where --validate says all checks pass, status.md says Next: no steps left in plan.md, and --session-start prints no derived-next line at all
touches:    bin/moltke.py inv_3_steps_in_plan; tests/test_s003_invariants.py; adocs/specs.md
excludes:   changing plan_order itself, which S045 settled and which this brings INV-3 into line with
decisions:
closes:     2026-08-07_adversarial.2-F02
blocks:
paused_by:
done:      2026-08-07: INV-3 reads plan_order, so it and derived_next share one definition of listed in plan.md — a list entry — and a step named only in the description is reported rather than silently unreachable. Prose ids are checked in neither direction, and the reverse message drops the phantom-is-next claim S045 falsified. 3 tests, red observed. Suite 236 OK, --validate green, finding fixture re-measured. README test count 233 to 236; MANUAL needed no change, it never described INV-3 by direction; templates/adocs/plan.md restated so a user writing their first plan sees the one rule.
