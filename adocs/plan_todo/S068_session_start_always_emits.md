id:         S068
goal:       --session-start always emits its JSON channel
accepts:    --session-start emits its hookSpecificOutput JSON on every path, including when a read fails, so the one channel that reaches the model is never silent on an exit 0; the error text rides in additionalContext rather than only on stderr; red observed with empty stdout on the finding's fixture
touches:    bin/moltke.py mode_session_start and the main backstop; tests/test_s005_hooks.py
excludes:   making --session-start blocking, which the hook contract forbids
decisions:  
closes:     2026-08-08_adversarial.2-F02
blocks:
paused_by:
done:
