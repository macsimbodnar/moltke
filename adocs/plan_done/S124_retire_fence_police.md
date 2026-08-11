id:         S124
goal:       INV-13, INV-14, INV-16 retired; stripping stays (DEC-047)
accepts:    acceptance criteria, testable
touches:    areas of the codebase
excludes:   explicitly out of scope
decisions:
closes:
blocks:
paused_by:
done:      2026-08-11: INV-13, INV-14 and INV-16 are retired (DEC-047), numbers never reused; strip_guidance is untouched so quoting stays safe. Nothing blocks on fence counts any more: the one real consequence of a swallowed finding surfaces in --audit list as hidden, exit 1 until the fence closes, and the planning nudge keeps staying quiet when a directive exists on disk in any form — now via _raw_prime_directive instead of the retired invariant, whose shared PRIME_DIRECTIVE_SECTION regex the first cut took with it and the suite caught. Police test classes deleted deliberately, the report-hiding class retargeted to --audit list, CHEAP_CHECKS shrinks. Suite 398 OK, --validate green. README count updated; MANUAL's fence section rewritten to the non-blocking model; specs marks all three retired.
author:    Maksym Bodnar
