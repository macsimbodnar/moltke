id:         S068
goal:       --session-start always emits its JSON channel
accepts:    --session-start emits its hookSpecificOutput JSON on every path, including when a read fails, so the one channel that reaches the model is never silent on an exit 0; the error text rides in additionalContext rather than only on stderr; red observed with empty stdout on the finding's fixture
touches:    bin/moltke.py mode_session_start and the main backstop; tests/test_s005_hooks.py
excludes:   making --session-start blocking, which the hook contract forbids
decisions:  
closes:     2026-08-08_adversarial.2-F02
blocks:
paused_by:
done:      2026-08-08: --session-start prints its JSON envelope on every path, with a read failure carried inside additionalContext. The whole payload was built before the single print, so one unreadable path lost all of it and the hook exited 0 with empty stdout — the one combination that cannot be seen, since a zero-exit hook's stderr reaches nobody, which is why S014 put the prompt-failure breadcrumb on this channel. session_context_lines builds the payload and the mode owns the envelope, so the output contract is kept where it is known rather than by a backstop. 2 tests, red observed with a JSONDecodeError against empty stdout, for a directory and a broken symlink. Suite 326 OK, --validate green. README test count 324 to 326; MANUAL needed no change, since it documents the channel and not its failure mode; specs gained a dated note.
