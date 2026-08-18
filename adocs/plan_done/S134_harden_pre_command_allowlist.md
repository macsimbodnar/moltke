id:         S134
goal:       the primitive must be the executed command, not a substring anywhere in it
accepts:    a persistent arm whose command merely mentions the primitive — in a trailing comment, or echoed before a hand-composed follow — is refused exactly as the bare leak is, observed red first; the primitive itself still passes, with and without a leading interpreter and inside a `bash -c`; MOLTKE_UNBOUNDED_OK stays the one escape and is still honoured; the refusal names the condition (INV-12)
touches:    bin/moltke.py mode_pre_command, tests/test_s130_precommand.py
excludes:   parsing arbitrary shell grammar; the single-match branch, which this bypass never reached
decisions:  DEC-049, DEC-051
closes:     2026-08-18_adversarial-F04
blocks:
paused_by:
done:      The persistent-arm lint asked whether the command *contained* the substring moltke ... --watch, so a comment mentioning the primitive — the natural thing for an agent to write next to a leak — silently disabled it and armed exactly the watcher DEC-049 targets. Reproduced red first as two forms, a trailing comment and an echo ahead of a hand-composed follow, both exit 0 where the bare leak exits 2. Replaced with a shlex tokenizer (quote-aware, comments stripped, punctuation_chars) asking whether --watch is what runs: no shell operator anywhere, one bash -c unwrap, an optional leading interpreter, and moltke.py first. The primitive's own 'RUN-(DONE|FAILED)' survives because it is quoted, which is why this is tokenized and not scanned; unparseable refuses rather than waves through. MOLTKE_UNBOUNDED_OK is checked before this and stays the one escape, comment and all. Closes 2026-08-18_adversarial-F04 (status flips on the S138 re-run, per §9).
author:    Maksym Bodnar
