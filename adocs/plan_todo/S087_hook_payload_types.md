id:         S087
goal:       a malformed hook payload refuses instead of raising
accepts:    a hook payload whose nested fields are not the expected types refuses or ignores them rather than raising: --pre-write exits 1 there, which is non-blocking, so the write fence fails open; --log-prompt must stay exit 0 whatever arrives, since blocking erases the prompt; red observed with the finding's payloads, and the reachability question stated rather than assumed
touches:    bin/moltke.py hook_input and its callers; tests/test_s005_hooks.py
excludes:   validating payload fields moltke does not read
decisions:  
closes:     2026-08-08_adversarial.3-F08
blocks:
paused_by:
done:
