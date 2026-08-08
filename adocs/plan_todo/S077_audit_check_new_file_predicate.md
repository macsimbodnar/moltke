id:         S077
goal:       --audit check shares one definition of newly here
accepts:    --audit check shares one definition of newly here with the Stop gates: _is_new_file keeps the pre-S050 predicate, so a new regression test staged and then edited is reported as unexpected contamination when it is exactly what the fence permits; red observed with the staged-then-edited test
touches:    bin/moltke.py _is_new_file and audit_check; tests/test_s008_audit.py
excludes:   widening what the reviewer may write
decisions:  
closes:     2026-08-08_adversarial.2-F11
blocks:
paused_by:
done:
