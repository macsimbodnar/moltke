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
done:
