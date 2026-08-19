id:         S146
goal:       MOLTKE_UNBOUNDED_OK covers the persistent-arm rule only, never the follow refusal
accepts:    MOLTKE_UNBOUNDED_OK no longer suppresses the single-match-follow refusal; that form is refused with the absence of an escape stated in the message; the persistent-arm escape still works for a genuinely unbounded stream; red observed first
touches:    bin/moltke.py mode_pre_command branch order, specs.md INV-17 wording if it moves
excludes:   widening what counts as a follow
decisions:
closes:     2026-08-19_adversarial-F06
blocks:
paused_by:
done:
