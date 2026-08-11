id:         S115
goal:       --step unpause says what actually happened
accepts:    Clearing a self-pause or a ring says so; clearing a phantom says the
            pauser had no step file; clearing a resolved pause says it resolved.
            No message describes a file the command just edited as nonexistent.
            A test asserts the self-pause message; it fails today.
touches:    bin/moltke.py step_unpause; tests/test_s003_invariants.py
excludes:   the refusal messages, which are correct
decisions:
closes:     2026-08-11_adversarial-F04
blocks:
paused_by:
done:      2026-08-11: --step unpause says what actually happened, closing 2026-08-11_adversarial-F04. The success message was one sentence for every case — the phantom wording — so clearing a self-pause described the file the command had just edited as having no step file in any plan directory. The reason now routes by the kind unresolvable_pauses returned: phantom names the missing file, stale says the pause resolved, a ring names the ring, and a self-pause is named as what it is. Most of the routing landed inside S114's shared-function change; this step's own red was the self-pause wording, observed as the generic ring sentence before the fix. 1 test. Suite 452 OK, --validate green. README test count 451 to 452; MANUAL checked, no change — it documents the refusals, which were already correct.
