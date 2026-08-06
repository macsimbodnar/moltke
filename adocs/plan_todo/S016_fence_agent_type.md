id:         S016
goal:       reviewer fence matches the scoped agent_type
accepts:    the observed agent_type is logged once from a real spawn before the match is chosen, since suffix matching fixes a namespaced value but not an absent field; a reviewer write outside the allowed set is blocked for both 'adversarial_reviewer' and 'moltke:adversarial_reviewer'; unrelated subagents and the main thread are unaffected; re-probed with a live plugin spawn attempting one write outside adocs/audit/, not with synthetic payloads alone, because trusting a self-authored payload is exactly the vacuity F02 caught; the MANUAL known issue is narrowed to the residual risk rather than removed
touches:    bin/moltke.py REVIEWER_AGENT match in mode_pre_write; tests/test_s008_audit.py TestReviewerWriteFence; MANUAL.md
excludes:   fail-closed on unrecognised subagents, rejected because it would block unrelated agents from writing anywhere; widening the allowed path set, which is S017
decisions:
closes:     2026-08-06_adversarial-F02
blocks:
paused_by:
done:
