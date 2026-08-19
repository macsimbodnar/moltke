id:         S150
goal:       INV-11's marker-gate test derives its mode list from the parser, with a named exempt set
accepts:    the INV-11 marker-gate test derives its mode list from build_parser() and names an explicit exempt set, so adding a mode without exempting it fails; specs.md INV-11 lists the same exemptions; red observed first against today's six-of-thirteen coverage
touches:    the INV-11 test, tests/surface.py if the derivation is shared, specs.md INV-11 wording
excludes:   changing which modes are actually exempt from the marker gate
decisions:
closes:     2026-08-19_adversarial-F10
blocks:
paused_by:
done:
