id:         S101
goal:       a malformed agent_type is fenced, not mistaken for the main thread
accepts:    --pre-write with `"agent_type": ["moltke:adversarial_reviewer"]` and a
            file_path outside the fence exits 2 and prints the fence message, as
            the string form already does.
            Absent stays absent: a payload with no agent_type key is the main
            thread and is not fenced, which is S016's rule and must not change.
            The distinction is between absent and malformed, not between string
            and non-string, so a payload whose agent_type is a number or a mapping
            is fenced too rather than passed through.
            The plan_done/ and step-file rules keep running for every payload
            shape, which is S087's fix and has its own tests.
            A test with a list-valued agent_type asserts exit 2; it fails without
            the fix. S087's well-formed-payload test stays as the non-vacuity
            anchor.
touches:    bin/moltke.py payload_str or a sibling helper, mode_pre_write;
            tests/test_s005_hooks.py
excludes:   changing what reviewer_may_write permits; treating the fence as a
            guarantee, which DEC-022 explicitly does not — the reviewer holds Bash
            and --audit check is what reconciles a run
decisions:  DEC-022
closes:     2026-08-09_adversarial-F05
blocks:
paused_by:
done:      2026-08-09: --pre-write distinguishes an absent agent_type from a malformed one and fences the malformed, closing 2026-08-09_adversarial-F05. S087 made payload_str return empty for anything that is not a string, which stopped the crash and left the fence reading a list-valued agent_type as the main thread, never fenced, so a reviewer payload of that shape wrote bin/moltke.py at exit 0 — a wrong pass, which is silent, in place of a wrong block, which is loud. JSON null is read as absent rather than malformed, deliberately: it is how a payload says no value, and fencing it would block every main-thread write if that is ever how no agent is encoded, which is a false block on the common path against a shape nobody has observed. Nothing establishes that Claude Code sends any of these; this is a property of the code, not a reproduction. DEC-022 is unchanged — the fence is a fast clear failure, not the guarantee, since the reviewer holds Bash and --audit check reconciles the run. 6 tests, red observed on six subtests; two are non-vacuity anchors holding the absent and null cases open. Suite 435 OK, --validate green. README test count 429 to 435; MANUAL checked, no change — its --pre-write row describes the fence by what it permits, which is unchanged; specs gained a dated note.
