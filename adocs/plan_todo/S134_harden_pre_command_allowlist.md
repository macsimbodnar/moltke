id:         S134
goal:       the primitive must be the executed command, not a substring anywhere in it
accepts:    a persistent arm whose command merely mentions the primitive — in a trailing comment, or echoed before a hand-composed follow — is refused exactly as the bare leak is, observed red first; the primitive itself still passes, with and without a leading interpreter and inside a `bash -c`; MOLTKE_UNBOUNDED_OK stays the one escape and is still honoured; the refusal names the condition (INV-12)
touches:    bin/moltke.py mode_pre_command, tests/test_s130_precommand.py
excludes:   parsing arbitrary shell grammar; the single-match branch, which this bypass never reached
decisions:  DEC-049, DEC-051
closes:     2026-08-18_adversarial-F04
blocks:
paused_by:
done:
