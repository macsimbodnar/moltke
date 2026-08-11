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
done:
