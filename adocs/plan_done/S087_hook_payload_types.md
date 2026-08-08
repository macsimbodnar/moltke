id:         S087
goal:       a malformed hook payload refuses instead of raising
accepts:    a hook payload whose nested fields are not the expected types refuses or ignores them rather than raising: --pre-write exits 1 there, which is non-blocking, so the write fence fails open; --log-prompt must stay exit 0 whatever arrives, since blocking erases the prompt; red observed with the finding's payloads, and the reachability question stated rather than assumed
touches:    bin/moltke.py hook_input and its callers; tests/test_s005_hooks.py
excludes:   validating payload fields moltke does not read
decisions:  
closes:     2026-08-08_adversarial.3-F08
blocks:
paused_by:
done:      2026-08-08: nested hook payload fields are read through payload_str, which returns empty for anything that is not a string. Only the top level was checked and every consumer assumed the rest, so a tool_input that is a string or an agent_type that is a list killed --pre-write — and a PreToolUse hook that dies exits 1, which is non-blocking, so the write it was judging proceeded: the reviewer fence and the plan_done refusal failing open, the direction S016 named as wrong. A prompt of the wrong type is coerced rather than dropped, because logging must never lose what the user typed. Whether Claude Code sends these shapes is not established, and the fence no longer depends on it. 4 tests, red observed on three payload shapes. Suite 376 OK, --validate green. README test count already updated in S086 to 376; MANUAL claim that no mode ends in a traceback is true again; specs gained a dated note.
