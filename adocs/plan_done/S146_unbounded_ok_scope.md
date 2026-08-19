id:         S146
goal:       MOLTKE_UNBOUNDED_OK covers the persistent-arm rule only, never the follow refusal
accepts:    MOLTKE_UNBOUNDED_OK no longer suppresses the single-match-follow refusal; that form is refused with the absence of an escape stated in the message; the persistent-arm escape still works for a genuinely unbounded stream; red observed first
touches:    bin/moltke.py mode_pre_command branch order, specs.md INV-17 wording if it moves
excludes:   widening what counts as a follow
decisions:
closes:     2026-08-19_adversarial-F06
blocks:
paused_by:
done:      2026-08-19 The escape hatch is now read after the single-match-follow branch, not before it, so MOLTKE_UNBOUNDED_OK exempts the persistent-arm rule only. INV-17's word was already "always" and DEC-051's was "bounded or not", while the code let one comment token switch off the one refusal that has no legitimate form behind it — and the persistent branch's own message teaches that token to everyone it blocks. The refusal now says the token does not reach this form and why: -m N asks for one match, the escape is for a genuinely unbounded stream. Closes 2026-08-19_adversarial-F06. Red observed first on three of four new tests; the fourth is the non-vacuity anchor, refusing the same stream without the token and passing with it. specs INV-17, MANUAL and AGENTS.md §12 (template identical) state the scope; README's test count was stale at 452 and now reads 476.
author:    Maksym Bodnar
