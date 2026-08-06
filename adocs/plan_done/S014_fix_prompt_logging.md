id:         S014
goal:       prompt logging never fails silently
accepts:    a --log-prompt in a marked repo whose adocs/ does not exist still records the prompt; a failed worklog append is reported through SessionStart additionalContext, the only channel that reaches the model on a zero exit; red observed and recorded before the fix
touches:    bin/moltke.py mode_log_prompt and mode_session_start; tests/test_s005_hooks.py
excludes:   worklog rotation or size limits; the recap gate (S015); the secret-shape check (S022)
decisions:
closes:     2026-08-06_adversarial-F14
blocks:
paused_by:
done:      2026-08-06: mkdir before append plus a .git breadcrumb reported once through SessionStart additionalContext; 4 tests in test_s005_hooks.py, 3 observed red first, suite 116 OK, --validate green. README test count updated to 116; MANUAL known issue narrowed from silent loss to unrecoverable-but-loud, F01 entry retitled to one hook. F14 stays planned until S027 re-runs the audit; the fix is inert in live sessions until 0.3.0 is installed.
