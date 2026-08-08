id:         S063
goal:       INV-13 scans every file strip_guidance is pointed at, specs.md included
accepts:    adocs/specs.md is in INV-13's scanned list, since S028 made it a strip_guidance input through prime_directive, so an odd marker count there is reported; two unclosed fences hiding the prime directive no longer leave --validate and --stop green while --session-start nags about a planning phase that is finished; the list is derived from, or checked against, what actually reads files through strip_guidance, so the next scanner added does not repeat this; red observed with the fenced prime directive and the permanent nudge
touches:    bin/moltke.py inv_13_balanced_fences and its scanned list; tests/test_s033_fences.py
excludes:   INV-14's heading rule, which is scoped to audit reports by DEC-033
decisions:
closes:     2026-08-08_adversarial-F04
blocks:
paused_by:
done:      2026-08-08: INV-13 scans stripped_files, one list derived from the readers rather than written beside them, so adocs/specs.md — which S028 made a strip_guidance consumer through prime_directive — is guarded like the rest, and every whole-file read goes through read_stripped so a new call site pairing strip_guidance with read_text fails a test instead of surfacing in an audit. INV-16 covers the half parity cannot reach: two example fences with their closers removed are an even count, so it compares what specs.md states against what survives stripping, exactly as INV-14 does for a finding heading. The planning nudge stays quiet in that case, because asking for a directive already on disk sends the user to rewrite it rather than close the fence. Deviation from touches: a new invariant, and the S028 nudge test re-targeted rather than relaxed, since the behaviour changed deliberately. 6 tests, red observed on all four behaviours. Suite 302 OK, --validate green. README test count 297 to 302; MANUAL's fence entry gained INV-16; specs gained the invariant and a dated note.
