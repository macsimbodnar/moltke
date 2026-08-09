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
done:
