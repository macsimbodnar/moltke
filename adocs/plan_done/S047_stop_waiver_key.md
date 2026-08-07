id:         S047
goal:       the Stop deadlock waiver cannot become an off switch
accepts:    the per-turn key comes from a field the payload is known to carry, with the live observation recorded in decisions.md the way S016 did for agent_type, or the waiver is redesigned so an absent key cannot make the counter global; eight consecutive stops on a repository with one unfixed violation do not read 2 2 2 0 0 0 0 0; the waived turn still prints the problems, so a user who hits the cap is told what was wrong rather than only that they were waved through; the counter resets when the problem set changes, not only when it empties; red observed with the finding's transcript and with the two fail-open routes, a JSONDecodeError payload and a tty invocation
touches:    bin/moltke.py mode_stop and _stop_state_path; adocs/decisions.md; adocs/specs.md; tests/test_s005_hooks.py TestStop
excludes:   removing the cap, which INV-12 and DEC-006 require; blocking forever, which is the deadlock the cap exists to prevent
decisions:
closes:     2026-08-07_adversarial.2-F01
blocks:
paused_by:
done:      2026-08-07: the Stop waiver counts retries within one turn, keyed on payload fields when present plus the worklog's prompt-heading count, which advances once per turn regardless of the payload; the count resets when the problem set changes and the waived turn prints the problems. DEC-029 records the choice and the three rejected alternatives. 5 tests, red observed as the finding's own sequence. Suite 233 OK, --validate green, transcript re-measured. README test count 228 to 233; MANUAL gained an entry on the cap; specs amended in place with the superseded 'same prompt' wording marked.
