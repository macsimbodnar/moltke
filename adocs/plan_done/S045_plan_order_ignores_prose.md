id:         S045
goal:       plan order comes from the list, not from prose that happens to name an id
accepts:    derived_next reads step ids from plan.md's ordered list only, so an id mentioned in the description above it does not become the next step; INV-3's reverse direction keeps reading the whole file, since a prose id with no step file is still a typo worth reporting; red observed with the real case that produced this step — a paragraph reading 'ahead of the feature work S028, S029, and S031' above a list starting at S034 made --step status write 'Next: S028' with --validate green, because both a phantom-free plan and a correct list still lose to document order
touches:    bin/moltke.py derived_next; tests/test_s003_invariants.py; tests/test_s007_step.py; adocs/specs.md
excludes:   validating plan.md numbering or detecting duplicate list entries; changing INV-3
notes:      this file already carries three prose ids that are harmless only because those steps are done — S001 and S002 in the description, and S012 inside S010's list entry. They are the natural fixtures: with any of them not in plan_done/, today's derived_next would return it.
decisions:
closes:
blocks:
paused_by:
done:      2026-08-07: derived_next reads plan order from list entries only, via a new plan_order; INV-3 still scans the whole file in both directions. 4 tests plus a live probe on the real plan.md, red observed as 'S002' != 'S003'. Suite 177 OK, --validate green. README test count 173 to 177; MANUAL checked, no change needed — it never describes how plan order is parsed. templates/adocs/plan.md gained two sentences stating the rule where a user writes their list, which is beyond the step's touches but is where the rule has to be visible.
