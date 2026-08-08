id:         S063
goal:       INV-13 scans every file strip_guidance is pointed at, specs.md included
accepts:    adocs/specs.md is in INV-13's scanned list, since S028 made it a strip_guidance input through prime_directive, so an odd marker count there is reported; two unclosed fences hiding the prime directive no longer leave --validate and --stop green while --session-start nags about a planning phase that is finished; the list is derived from, or checked against, what actually reads files through strip_guidance, so the next scanner added does not repeat this; red observed with the fenced prime directive and the permanent nudge
touches:    bin/moltke.py inv_13_balanced_fences and its scanned list; tests/test_s033_fences.py
excludes:   INV-14's heading rule, which is scoped to audit reports by DEC-033
decisions:
closes:     2026-08-08_adversarial-F04
blocks:
paused_by:
done:
