id:         S014
goal:       prompt logging never fails silently
accepts:    a --log-prompt in a marked repo whose adocs/ does not exist still records the prompt; a failed worklog append is reported through SessionStart additionalContext, the only channel that reaches the model on a zero exit; red observed and recorded before the fix
touches:    bin/moltke.py mode_log_prompt and mode_session_start; tests/test_s005_hooks.py
excludes:   worklog rotation or size limits; the recap gate (S015); the secret-shape check (S022)
decisions:
closes:     2026-08-06_adversarial-F14
blocks:
paused_by:
done:
