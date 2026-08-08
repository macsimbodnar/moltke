id:         S077
goal:       --audit check shares one definition of newly here
accepts:    --audit check shares one definition of newly here with the Stop gates: _is_new_file keeps the pre-S050 predicate, so a new regression test staged and then edited is reported as unexpected contamination when it is exactly what the fence permits; red observed with the staged-then-edited test
touches:    bin/moltke.py _is_new_file and audit_check; tests/test_s008_audit.py
excludes:   widening what the reviewer may write
decisions:  
closes:     2026-08-08_adversarial.2-F11
blocks:
paused_by:
done:      2026-08-08: --audit check and the Stop gates share one definition of newly here. _is_new_file kept the pre-S050 predicate while _arrives_here learned that the index half decides, so AM — a red-first regression test staged and then refined, which is how one is actually written — was reported as contamination the reviewer had to justify, when a new file under tests/ is exactly what the fence permits. An edit to a test that already existed is still unexpected, since the fence allows new files and not patches to old ones. 2 tests, red observed with the AM shape. Suite 347 OK, --validate green. README test count 345 to 347; MANUAL needed no change, since it describes what the check permits and that is now what it does; specs gained a dated note.
